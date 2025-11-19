class Alert:
    def __init__(self, version: str =  "<\"1.0\" encoding=\"UTF-8\"?>", \
                record: str = "<xmlns:dc=\"http://purl.org/dc/elements/1.1/\"", \
                title: str = "", creator: str = "", subject: str = "", \
                description: str = "", publisher: str = "", contributor: str = "", \
                date: str = "", type: str = "", format: str = "", identifier: str = "", \
                source: str = "", language: str = "", relation: str = "", \
                coverage: str = "", rights: str = "" ):
        self.version: str = version
        self.record: str = record        
        self.title: str = title
        self.creator: str = creator
        self.subject: str = subject
        self.description: str = description
        self.publisher: str = publisher
        self.contributor: str = contributor
        self.date: str = date
        self.type: str = type
        self.format: str = format
        self.identifier: str = identifier
        self.source: str = source
        self.language: str = language
        self.relation: str = relation
        self.coverage: str = coverage
        self.rights: str = rights

    def __str__(self) -> str:
        return self.get_metadata()

    def get_metadata(self) -> str:
        return f"""<?xml version={self.version}>\
        \n<record xmlns:dc={self.record}>"\
        \n    <dc:title>{self.title}</dc:title>\
        \n    <dc:creator>{self.creator}</dc:creator>\
        \n    <dc:subject>{self.subject}</dc:subject>\
        \n    <dc:description>{self.description}</dc:description>\
        \n    <dc:publisher>{self.publisher}</dc:publisher>\
        \n    <dc:contributor>{self.contributor}</dc:contributor>\
        \n    <dc:date>{self.date}</dc:date>\
        \n    <dc:type>{self.type}</dc:type>\
        \n    <dc:format>{self.format}</dc:format>\
        \n    <dc:identifier>{self.identifier}</dc:identifier>\
        \n    <dc:source>{self.identifier}</dc:source>\
        \n    <dc:language>{self.language}</dc:language>\
        \n    <dc:relation>{self.relation}</dc:relation>\
        \n    <dc:coverage>{self.coverage}</dc:coverage>\
        \n    <dc:rights>{self.rights}</dc:rights>\
        \n</record>"""
    
if __name__ == "__main__":
    alert = Alert(
        title="Dengue Outbreak Alert",
        creator="Arboviral Epidemic Predictor",
        subject="Dengue Fever",
        description="This alert indicates a potential dengue outbreak in the specified region.",
        publisher="Health Department",
        date="2024-06-01",
        type="Alert",
        format="XML",
        identifier="alert-20240601-001",
        source="Epidemiological Data",
        language="en",
        relation="Dengue Surveillance",
        coverage="Region XYZ",
        rights="All rights reserved."
    )
    print(alert.get_metadata())