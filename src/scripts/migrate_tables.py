from src.db.database import Base, engine

def create_tables():
    from src.models.chat import ChatTopic, ChatConversation, ChatMessage
    from src.models.users import Users
    
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
    print("Database tables created successfully.")
