from sqlalchemy import Integer, String, DateTime, Text, func

from . import db
from config import DBTableConfig

class links(db.Model):
    ID_L = db.Column(Integer, primary_key=True)
    Scrape_DateTime = db.Column(DateTime(timezone=False),default=func.now())
    Link = db.Column(Text)
    Scrape_Status = db.Column(Text)
    Link_Health_Status = db.Column(Text,
                                    default=DBTableConfig.links_table_link_health_healthy)