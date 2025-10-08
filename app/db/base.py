# استيراد جميع النماذج حتى يتمكن Alembic من اكتشافها

# For run alembic
# alembic revision --autogenerate -m "commit"
# alembic upgrade head

from app.db.session import Base
from app.models.post import Post
from app.models.user import User
