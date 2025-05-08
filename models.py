
from datetime import datetime

from app import db
    
class ImageView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    processed_date = db.Column(db.DateTime, default=datetime.utcnow)
    red_pixels = db.Column(db.Integer, default=0)
    green_pixels = db.Column(db.Integer, default=0)
    blue_pixels = db.Column(db.Integer, default=0)
    other_pixels = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'filename': self.filename,
            'processed_date': self.processed_date.strftime('%d/%m/%Y %H:%M:%S'),
            'red_pixels': self.red_pixels,
            'green_pixels': self.green_pixels,
            'blue_pixels': self.blue_pixels,
            'other_pixels': self.other_pixels
        }
