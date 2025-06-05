from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Date, Time, ForeignKey, Text, Enum, ARRAY
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, date, time
from pydantic import BaseModel, ConfigDict
from typing import Optional, List

Base = declarative_base()

# Common Pydantic model configuration
class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            time: lambda v: v.isoformat()
        }
    )

# SQLAlchemy ORM Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    roadmaps = relationship("Roadmap", back_populates="user")
    preferences = relationship("UserPreference", back_populates="user", uselist=False)

class Roadmap(Base):
    __tablename__ = "roadmaps"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    budget_total = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="roadmaps")
    days = relationship("RoadmapDay", back_populates="roadmap", cascade="all, delete-orphan")
    tickets = relationship("Ticket", back_populates="roadmap", cascade="all, delete-orphan")
    accommodations = relationship("Accommodation", back_populates="roadmap", cascade="all, delete-orphan")
    places = relationship("Place", back_populates="roadmap", cascade="all, delete-orphan")
    food_places = relationship("FoodPlace", back_populates="roadmap", cascade="all, delete-orphan")

class RoadmapDay(Base):
    __tablename__ = "roadmap_days"
    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id"))
    day_index = Column(Integer)
    date = Column(Date)
    summary = Column(Text)
    
    # Relationships
    roadmap = relationship("Roadmap", back_populates="days")
    tasks = relationship("RoadmapTask", back_populates="day", cascade="all, delete-orphan")

class RoadmapTask(Base):
    __tablename__ = "roadmap_tasks"
    id = Column(Integer, primary_key=True, index=True)
    roadmap_day_id = Column(Integer, ForeignKey("roadmap_days.id"))
    type = Column(String)
    title = Column(String)
    description = Column(Text)
    start_time = Column(Time)
    end_time = Column(Time)
    linked_id = Column(Integer)
    link_type = Column(String)
    
    # Relationships
    day = relationship("RoadmapDay", back_populates="tasks")

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id"))
    type = Column(String)
    from_ = Column("from", String)
    to = Column(String)
    departure = Column(DateTime)
    arrival = Column(DateTime)
    price = Column(Integer)
    provider_url = Column(String)
    
    # Relationships
    roadmap = relationship("Roadmap", back_populates="tickets")

class Accommodation(Base):
    __tablename__ = "accommodations"
    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id"))
    name = Column(String)
    check_in = Column(DateTime)
    check_out = Column(DateTime)
    price_total = Column(Integer)
    location = Column(String)
    provider_url = Column(String)
    
    # Relationships
    roadmap = relationship("Roadmap", back_populates="accommodations")

class Place(Base):
    __tablename__ = "places"
    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id"))
    name = Column(String)
    category = Column(String)
    location = Column(String)
    duration_min = Column(Integer)
    rating = Column(Float)
    url = Column(String)
    
    # Relationships
    roadmap = relationship("Roadmap", back_populates="places")

class FoodPlace(Base):
    __tablename__ = "food_places"
    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id"))
    name = Column(String)
    category = Column(String)
    location = Column(String)
    avg_price = Column(Integer)
    rating = Column(Float)
    url = Column(String)
    
    # Relationships
    roadmap = relationship("Roadmap", back_populates="food_places")

class UserPreference(Base):
    __tablename__ = "user_preferences"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    food_type = Column(ARRAY(String))
    interests = Column(ARRAY(String))
    daily_budget = Column(Integer)
    accommodation_type = Column(String)
    walking_or_guided = Column(String)
    
    # Relationships
    user = relationship("User", back_populates="preferences")

# Pydantic Models
class UserBase(BaseSchema):
    email: str
    name: str

class UserCreate(UserBase):
    password: str
    type: str

class UserLogin(BaseSchema):
    email: str
    password: str

class User(UserBase):
    id: int
    created_at: datetime

class RoadmapBase(BaseSchema):
    title: str
    destination: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget_total: Optional[int] = None

class RoadmapCreate(RoadmapBase):
    pass

class Roadmap(RoadmapBase):
    id: int
    user_id: int
    created_at: datetime

class RoadmapDayBase(BaseSchema):
    day_index: int
    date: date
    summary: Optional[str] = None

class RoadmapDayCreate(RoadmapDayBase):
    pass

class RoadmapDay(RoadmapDayBase):
    id: int
    roadmap_id: int

class RoadmapTaskBase(BaseSchema):
    type: str
    title: str
    description: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    linked_id: Optional[int] = None
    link_type: Optional[str] = None

class RoadmapTaskCreate(RoadmapTaskBase):
    pass

class RoadmapTask(RoadmapTaskBase):
    id: int
    roadmap_day_id: int

class TicketBase(BaseSchema):
    type: str
    from_: str
    to: str
    departure: datetime
    arrival: datetime
    price: int
    provider_url: Optional[str] = None

class TicketCreate(TicketBase):
    pass

class Ticket(TicketBase):
    id: int
    roadmap_id: int

class AccommodationBase(BaseSchema):
    name: str
    check_in: datetime
    check_out: datetime
    price_total: int
    location: str
    provider_url: Optional[str] = None

class AccommodationCreate(AccommodationBase):
    pass

class Accommodation(AccommodationBase):
    id: int
    roadmap_id: int

class PlaceBase(BaseSchema):
    name: str
    category: str
    location: str
    duration_min: int
    rating: float
    url: Optional[str] = None

class PlaceCreate(PlaceBase):
    pass

class Place(PlaceBase):
    id: int
    roadmap_id: int

class FoodPlaceBase(BaseSchema):
    name: str
    category: str
    location: str
    avg_price: int
    rating: float
    url: Optional[str] = None

class FoodPlaceCreate(FoodPlaceBase):
    pass

class FoodPlace(FoodPlaceBase):
    id: int
    roadmap_id: int

class UserPreferenceBase(BaseSchema):
    food_type: List[str]
    interests: List[str]
    daily_budget: int
    accommodation_type: str
    walking_or_guided: str

class UserPreferenceCreate(UserPreferenceBase):
    pass

class UserPreference(UserPreferenceBase):
    id: int
    user_id: int

class Token(BaseSchema):
    access_token: str
    type: str