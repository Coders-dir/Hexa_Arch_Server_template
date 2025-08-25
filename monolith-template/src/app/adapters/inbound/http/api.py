from fastapi import APIRouter, FastAPI
from src.app.adapters.inbound.http.controllers import user_controller
from src.app.adapters.inbound.http.controllers import user_controller_supabase
from src.app.adapters.inbound.http.controllers import admin_controller

router = APIRouter()

router.include_router(user_controller.router, prefix="/users", tags=["users"])
router.include_router(user_controller_supabase.router, prefix="/supabase", tags=["supabase"])
router.include_router(admin_controller.router, prefix="", tags=["admin"])


def init_app(app: FastAPI):
	# initialize quota manager and attach middleware
	from src.app.adapters.outbound.redis_quota import QuotaManager
	from src.app.adapters.inbound.http.middleware.dispatcher_middleware import DispatcherMiddleware
	import asyncio
	from src.app.adapters.outbound.api_key_repo import ApiKeyRepo
	qm = QuotaManager()

	# API key repo instance (initialized on startup)
	app.state.api_key_repo = ApiKeyRepo()

	async def _startup():
		await qm.init()
		app.state.quota_manager = qm
		# initialize api key repo pool
		try:
			await app.state.api_key_repo.init()
		except Exception:
			# if pool init fails, keep repo available; methods will fallback to per-call connections
			pass

	async def _shutdown():
		await qm.close()

	app.add_event_handler("startup", _startup)
	# start a simple scheduler worker

	async def _scheduler():
		qm_local = qm
		while True:
			try:
				# priority queue pop (delayed + priority)
				val = await qm_local.pop_queue_priority("dispatcher:priority_queue")
				if val:
					# simulate processing
					print("dispatcher processed", val)
				else:
					await asyncio.sleep(0.2)
			except asyncio.CancelledError:
				break
			except Exception:
				await asyncio.sleep(1)

	_scheduler_task = None

	async def _start_scheduler():
		nonlocal _scheduler_task
		_scheduler_task = asyncio.create_task(_scheduler())

	async def _stop_scheduler():
		nonlocal _scheduler_task
		if _scheduler_task:
			_scheduler_task.cancel()
			try:
				await _scheduler_task
			except Exception:
				pass

	app.add_event_handler("startup", _start_scheduler)
	app.add_event_handler("shutdown", _stop_scheduler)
	app.add_event_handler("shutdown", _shutdown)
	# add middleware (will check app.state.quota_manager at runtime)
	app.add_middleware(DispatcherMiddleware)
