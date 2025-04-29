from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(256), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)

    # Relaciones
    posts = relationship("Post", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    likes = relationship("Like", back_populates="user")

    # Seguidores (followers) que siguen a este usuario
    followers = relationship(
        "Follower",
        foreign_keys="Follower.followed_id",
        back_populates="followed"
    )

    # Usuarios (followings) a los que este usuario sigue
    followings = relationship(
        "Follower",
        foreign_keys="Follower.follower_id",
        back_populates="follower"
    )

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # No incluimos password por seguridad
            "is_active": self.is_active
        }


class Post(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    image_url: Mapped[str] = mapped_column(String(256), nullable=False)
    caption: Mapped[str] = mapped_column(String(500), nullable=True)
    location: Mapped[str] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)

    # Relaciones
    user = relationship("User", back_populates="posts")
    comments = relationship(
        "Comment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="post",
                         cascade="all, delete-orphan")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "image_url": self.image_url,
            "caption": self.caption,
            "location": self.location,
            "created_at": self.created_at,
            "comments_count": len(self.comments),
            "likes_count": len(self.likes)
        }


class Comment(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"))
    text: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)

    # Relaciones
    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "post_id": self.post_id,
            "text": self.text,
            "created_at": self.created_at
        }


class Like(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)

    # Relaciones
    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "post_id": self.post_id,
            "created_at": self.created_at
        }


class Follower(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    follower_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"))  # Usuario que sigue
    followed_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"))  # Usuario que es seguido
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)

    # Relaciones
    follower = relationship("User", foreign_keys=[
                            follower_id], back_populates="followings")
    followed = relationship("User", foreign_keys=[
                            followed_id], back_populates="followers")

    def serialize(self):
        return {
            "id": self.id,
            "follower_id": self.follower_id,
            "followed_id": self.followed_id,
            "created_at": self.created_at
        }


# Esto genera el diagrama cuando ejecutas el archivo
if __name__ == "__main__":
    from eralchemy2 import render_er
    render_er(db.Model, 'diagram.png')
