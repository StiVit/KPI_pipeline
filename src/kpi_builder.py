import uuid

class KPIBuilder:
    def __init__(self):
        self.kpis = []

    def add_aggregation(self, name, column, operation, filters=None):
        kpi = {
            "id": self._generate_id(name),
            "name": name,
            "type": "aggregation",
            "column": column,
            "operation": operation,
            "filters": filters or []
        }
        self.kpis.append(kpi)

    def add_count(self, name, filters=None):
        kpi = {
            "id": self._generate_id(name),
            "name": name,
            "type": "count",
            "filters": filters or []
        }
        self.kpis.append(kpi)

    def add_groupby(self, name, groupby, column, operation, filters=None):
        kpi = {
            "id": self._generate_id(name),
            "name": name,
            "type": "groupby",
            "groupby": groupby,
            "column": column,
            "operation": operation,
            "filters": filters or []
        }
        self.kpis.append(kpi)

    def add_mixed(self, name, kpi1_id, kpi2_id, operation):
        kpi = {
            "id": self._generate_id(name),
            "name": name,
            "type": "mixed",
            "ref_kpi_1": kpi1_id,
            "ref_kpi_2": kpi2_id,
            "operation": operation
        }
        self.kpis.append(kpi)
    
    def build(self):
        return {"kpis": self.kpis}
    
    def _generate_id(self, name):
        return name.lower().replace(" ", "_") + "_" + str(uuid.uuid4())[:6]
    

def test_config_gen():
    user_input = {  
        "type": "aggregation",
        "name": "Total Time",
        "column": "tempo_min",
        "operation": "sum",
        "filters": [
            {"column": "tempo_min", "operator": ">", "value": 10}
        ]
    }

    builder = KPIBuilder()

    builder.add_aggregation(
        name=user_input["name"],
        column=user_input["column"],
        operation=user_input['operation'],
        filters=user_input['filters']
    )

    return builder.build()