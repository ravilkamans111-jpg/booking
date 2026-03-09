class DataMapper:
    db_model = None
    schema = None

    @classmethod
    def map_to_domain_entity_pyd(cls, data):
        """From alchemy to pydantic"""
        return cls.schema.model_validate(data, from_attributes=True)

    @classmethod
    def map_to_persistence_entity_db(cls, data):
        """From pydantic to alchemy"""
        return cls.db_model(data.model_dump())
