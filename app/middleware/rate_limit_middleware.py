from fastapi import Request, status
from fastapi.responses import JSONResponse


from app.core.rate_limiter import rate_limiter


async def rate_limit_middleware(request: Request, call_next):
  # Example: Limit to 5 requests per minute per IP
  client_ip = request.client.host
  try:
    result = await rate_limiter(key=client_ip, limit=10, period=60)

  except Exception as e:
    detail = e.detail if isinstance(e.detail, dict) else {
        "error": str(e.detail)}
    response = JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS, content=detail)
    if isinstance(e.detail, dict):
      response.headers["X-RateLimit-Limit"] = str(e.detail.get('limit', 5))
      response.headers["X-RateLimit-Remaining"] = str(
          e.detail.get('remaining', 0))
      response.headers["X-RateLimit-Reset"] = str(e.detail.get('reset', 60))
    return response

  response = await call_next(request)
  response.headers["X-RateLimit-Limit"] = str(result['limit'])
  response.headers["X-RateLimit-Remaining"] = str(result['remaining'])
  response.headers["X-RateLimit-Reset"] = str(result['reset'])

  return response
