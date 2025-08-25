QUOTA_SCRIPT = '''
local key = KEYS[1]
local window = tonumber(ARGV[1])
local limit = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local bucket = key .. ':' .. math.floor(now / window)
local val = redis.call('INCR', bucket)
if val == 1 then redis.call('EXPIRE', bucket, window) end
if val <= limit then return 1 else return 0 end
'''
