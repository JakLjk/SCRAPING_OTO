from sqlalchemy import Integer, String, DateTime, Text, Boolean, func
from sqlalchemy.dialects.mysql import LONGTEXT

from . import db
from config import DBTableConfig

class links(db.Model):
    ID_L = db.Column(Integer, primary_key=True)
    Scrape_DateTime = db.Column(DateTime(timezone=False),default=func.now())
    Link = db.Column(Text)
    Scrape_Status = db.Column(Text)
    Link_Health_Status = db.Column(Text,
                                    default='')
    
class raw_offer_data(db.Model):
    ID_O = db.Column(Integer, primary_key=True)
    Scrape_DateTime = db.Column(DateTime(timezone=False),default=func.now())
    Raw_Data = db.Column(LONGTEXT)
    Used_Link = db.Column(Text)
    ETL_Performed_Status = db.Column(Text)

class offer_details_parsed(db.Model):
    ID_O_P = db.Column(Integer, primary_key=True)
    Parsing_DateTime = db.Column(DateTime(timezone=False),default=func.now())
    Link = db.Column(Text)
    Offer_Title = db.Column(Text)
    Offer_Price = db.Column(Text)
    Offer_Details = db.Column(Text)
    Equipment_Details = db.Column(Text)
    Coordinates = db.Column(Text)