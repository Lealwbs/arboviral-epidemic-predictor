from datetime import datetime, timezone


class Alert:
    def __init__(self, event: str = "Dengue", severity: str = "", certainly: str = "",    
                 year: str = "", month: str = "", city_name: str = "", city_code: str = ""):
        self.identifier = f"alert_{city_code}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}"
        self.sender = "Sistema de Alertas de Saúde Pública"
        self.sent = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.status = "Atual"
        self.msgType = "Alerta"
        self.scope = "Público"
        self.language = "pt-BR"
        self.category = "Arboviroses"
        self.event = event
        self.urgency = "None"
        self.severity = severity
        self.certainly = certainly
        self.headline = "Alerta de Surto Arboviral"
        self.description = "Indicação de potencial surto na região especificada."
        self.year = year
        self.month = month
        self.city_name = city_name
        self.city_code = city_code
        self.version = "\"1.0\" encoding=\"UTF-8\""
        self.namespace = "\"https://docs.oasis-open.org/emergency/cap/v1.2/CAP-v1.2-os.html\""

    def __str__(self):
        return self.get_metadata()

    def get_metadata(self) -> str:
        result: str = (
        f"<?xml version={self.version}?>\n"
        f"<alert xmlns={self.namespace}>\n"
        f"    <identifier>{self.identifier}</identifier>\n"
        f"    <sender>{self.sender}</sender>\n"
        f"    <sent>{self.sent}</sent>\n"
        f"    <status>{self.status}</status>\n"
        f"    <msgType>{self.msgType}</msgType>\n"
        f"    <scope>{self.scope}</scope>\n"
        f"    <info>\n"
        f"        <language>{self.language}</language>\n"
        f"        <category>{self.category}</category>\n"
        f"        <event>{self.event}</event>\n"
        f"        <urgency>{self.urgency}</urgency>\n"
        f"        <severity>{self.severity}</severity>\n"
        f"        <certainty>{self.certainly}</certainty>\n"
        f"        <headline>{self.headline}</headline>\n"
        f"        <description>{self.description}</description>\n"
        f"        <parameter>\n"
        f"            <valueName>year</valueName>\n"
        f"            <value>{self.year}</value>\n"
        f"        </parameter>\n"
        f"        <parameter>\n"
        f"            <valueName>month</valueName>\n"
        f"            <value>{self.month}</value>\n"
        f"        </parameter>\n"
        f"        <area>\n"
        f"            <areaDesc>{self.city_name}</areaDesc>\n"
        f"            <geocode>\n"
        f"                <valueName>IBGE</valueName>\n"
        f"                <value>{self.city_code}</value>\n"
        f"            </geocode>\n"
        f"        </area>\n"
        f"    </info>\n"
        f"</alert>")
        return result


if __name__ == "__main__":
    A = Alert(
        event="Dengue",
        severity="Alto Risco",
        certainly="100%",
        year="2024",
        month="06",
        city_name="Belo Horizonte",
        city_code="3106200"
    )

    print(A)