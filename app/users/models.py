from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base, str_uniq, int_pk


class User(Base):
    __tablename__ = "users"

    id: Mapped[int_pk]
    phone_number: Mapped[str_uniq]
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str_uniq]
    password: Mapped[str]

    # Исправлено: lazy="selectin" вместо "selectinload"
    roles = relationship("UserRoles", back_populates="user", lazy="selectin")

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"

    @property
    def is_admin(self) -> bool:
        return any(user_role.role.name == 'admin' for user_role in self.roles)


# Модель для описания роли
class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int_pk]
    name: Mapped[str_uniq]

    users = relationship("UserRoles", back_populates="role")  # Используйте имя класса, а не таблицы

    def __repr__(self):
        return f"Role(id={self.id}, name={self.name})"


# Связывающая таблица между User и Role
class UserRoles(Base):
    __tablename__ = "user_roles"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), primary_key=True)
    UniqueConstraint("user_id", "role_id", name="uq_user_role")

    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="users")
