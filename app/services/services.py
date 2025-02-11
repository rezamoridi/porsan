from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.models import User, Role, University, Department
from middleware.auth_middleware import AuthService
from dotenv import load_dotenv
import os
import logging
load_dotenv()


logger = logging.getLogger(__name__)

async def initialize_super_admin(db: Session) -> None:
    """
    Check if super admin exists, if not create one
    """
    try:
        universities_db = db.query(University).all()
        departments_db = db.query(Department).all()
        roles_db = db.query(Role).all()
        if not roles_db:
            user_role = Role(id=1, name="user", desc="normal_user")
            admin_role = Role(id=2, name="admin", desc="admin")
            super_admin_role = Role(id=3, name="superadmin", desc="owner")
            for role in [user_role,admin_role,super_admin_role]:
                db.add(role)
                db.commit()
        if not universities_db:
            university = University(id=1, name="lorestan-lu")
            db.add(university)
            db.commit()

        if not departments_db:
            department = Department(id=1, name="science")
            db.add(department)
            db.commit()
        # Check if any super admin exists
        super_admin = db.query(User).filter(User.role_id == 3).first()
        
        if not super_admin:
            logger.info("No super admin found. Creating default super admin...")
            
            # Create super admin user
            super_admin = User(
                username=os.getenv("FIRST_SUPERADMIN_USERNAME"),
                password=AuthService.get_password_hash(os.getenv("FIRST_SUPERADMIN_PASSWORD")),
                name="Super",
                lname="Admin",
                fa_name="Admin",
                sid = "11111111111",
                id_number="0000000000",  # Default ID number
                role_id=3,  # Super admin role
                status=True,
                phone_number="09000000000"  # Default phone number
            )
            
            db.add(super_admin)
            db.commit()
            logger.info("Super admin created successfully")
        
    except SQLAlchemyError as e:
        logger.error(f"Error creating super admin: {str(e)}")
        db.rollback()
        raise