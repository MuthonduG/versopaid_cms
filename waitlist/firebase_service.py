from django.conf import settings
from datetime import datetime
import uuid

class FirebaseWaitlistService:
    """Service class to handle Firebase Firestore operations for waitlist"""
    
    COLLECTION_NAME = 'waitlist'
    
    def __init__(self):
        if not settings.FIREBASE_INITIALIZED:
            raise Exception("Firebase is not initialized")
        self.db = settings.FIRESTORE_CLIENT
    
    def create_entry(self, data):
        """Create a new waitlist entry"""
        try:
            entry_id = str(uuid.uuid4())
            
            data['created_at'] = datetime.now()
            data['updated_at'] = datetime.now()
            data['id'] = entry_id
            
            data = {k: v for k, v in data.items() if v is not None}
            
            doc_ref = self.db.collection(self.COLLECTION_NAME).document(entry_id)
            doc_ref.set(data)
            
            return self._prepare_for_json(data)
        except Exception as e:
            raise Exception(f"Failed to create entry: {str(e)}")
    
    def get_entry_by_email(self, email):
        """Get waitlist entry by email"""
        try:
            docs = self.db.collection(self.COLLECTION_NAME)\
                         .where('email', '==', email)\
                         .limit(1)\
                         .stream()
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                return self._prepare_for_json(data)
            
            return None
        except Exception as e:
            raise Exception(f"Failed to get entry: {str(e)}")
    
    def get_entry_by_id(self, entry_id):
        """Get waitlist entry by ID"""
        try:
            doc_ref = self.db.collection(self.COLLECTION_NAME).document(entry_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return self._prepare_for_json(data)
            
            return None
        except Exception as e:
            raise Exception(f"Failed to get entry: {str(e)}")
    
    def get_all_entries(self, limit=100):
        """Get all waitlist entries"""
        try:
            docs = self.db.collection(self.COLLECTION_NAME)\
                         .limit(limit)\
                         .stream()
            
            entries = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                entries.append(self._prepare_for_json(data))
            
            entries.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            return entries
        except Exception as e:
            raise Exception(f"Failed to get entries: {str(e)}")
    
    def check_email_exists(self, email):
        """Check if email already exists"""
        try:
            docs = self.db.collection(self.COLLECTION_NAME)\
                         .where('email', '==', email)\
                         .limit(1)\
                         .stream()
            
            return any(True for _ in docs)
        except Exception as e:
            raise Exception(f"Failed to check email: {str(e)}")
    
    def update_entry(self, entry_id, data):
        """Update an existing entry"""
        try:
            data['updated_at'] = datetime.now()
            
            data = {k: v for k, v in data.items() if v is not None}
            
            doc_ref = self.db.collection(self.COLLECTION_NAME).document(entry_id)
            doc_ref.update(data)
            
            updated_doc = doc_ref.get()
            if updated_doc.exists:
                result = updated_doc.to_dict()
                result['id'] = updated_doc.id
                return self._prepare_for_json(result)
            
            return None
        except Exception as e:
            raise Exception(f"Failed to update entry: {str(e)}")
    
    def delete_entry(self, entry_id):
        """Delete an entry"""
        try:
            self.db.collection(self.COLLECTION_NAME).document(entry_id).delete()
            return True
        except Exception as e:
            raise Exception(f"Failed to delete entry: {str(e)}")
    
    def _prepare_for_json(self, data):
        """Convert datetime objects to strings for JSON serialization"""
        if not data:
            return data
        
        prepared = {}
        for key, value in data.items():
            if hasattr(value, 'isoformat'):  
                prepared[key] = value.isoformat()
            else:
                prepared[key] = value
        return prepared