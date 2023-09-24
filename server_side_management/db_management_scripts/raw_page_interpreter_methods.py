from ..webhook.db_model import raw_offer_data, offer_details_parsed
from ..webhook import db
from config import DBTableConfig, OperationTypes
from sqlalchemy.sql.expression import false


def get_raw_from_db():
    data = (raw_offer_data
            .query
            .with_for_update(skip_locked=True)
            .filter(raw_offer_data.ETL_Performed_Status == DBTableConfig.raw_data_table_etl_not_performed)
            ).first()
    if data:
        return data
    else:
        raise ValueError("No raw data to provided available")

def update_etl_status_performed(id, used_link, new_status):
    raw_data_row = (raw_offer_data
                    .query
                    .filter(raw_offer_data.ID_O == id)
                    .first())
    raw_data_row.ETL_Performed_Status = new_status
    db.session.commit()

def push_offer_details_parsed_to_db(link:str,
                           offer_title:str,
                           offer_price:str,
                           offer_details:str,
                           offer_equipment_details:str,
                           offer_coordinates:str):
    details = offer_details_parsed.query.filter(
        offer_details_parsed.Link == link).first()
    if details:
            print('////////////ARLEADY IN')
            print(link)
            print(type(link))
        # raise ValueError("Such details were already scraped")
            details.Link = link
            details.Offer_Title = offer_title
            details.Offer_Price = offer_price
            details.Offer_Details = offer_details
            details.Equipment_Details = offer_equipment_details
            details.Coordinates = offer_coordinates
            db.session.commit()
    else:
        new_details = offer_details_parsed(
            Link = link,
            Offer_Title = offer_title,
            Offer_Price = offer_price,
            Offer_Details = offer_details,
            Equipment_Details = offer_equipment_details,
            Coordinates = offer_coordinates)
        db.session.add(new_details)
        db.session.commit()