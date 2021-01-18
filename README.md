# Betacore Kafka Schema

A repo that allows for quick decode and encode.

# Avro
Please read 
[Avro Spec](https://avro.apache.org/docs/current/spec.html) for how to create schema
configuration.

## Decode
Allows Decoding of byte steam with the schema provided. If the schema is incorrect an error may be raised.

```python
from betacore.kafka.schema.avro import AvroSchema
message = {
    "test": "body"
}
schema = {
    "type": "record",
    "namespace": "betacore",
    "name": "Test entity",
    "fields": [
        {"name": "test", "type": "string"}
    ]
}
encoded: bytes = AvroSchema().encode(message, schema=schema)
actual: dict = AvroSchema().decode(encoded, schema=schema)
```
## Encode
Sample on how to encode with an avro schema. The message keys must be in the schema definition

```python
from betacore.kafka.schema.avro import AvroSchema
message = {
    "test": "body"
}
schema = {
    "type": "record",
    "namespace": "betacore",
    "name": "Test entity",
    "fields": [
        {"name": "test", "type": "string"}
    ]
}
encoded: bytes = AvroSchema().encode(message, schema=schema)
```
# Registry 
The registry is still in beta only get / decode operations are implemented. This functional may be broken.  

# Local Development
* Clone repo
* if using python virtual environment, which is strongly recommended, source the `venv` script.
* install packages
  * Required: `pip3 install -r requirements.txt`
  * Development: `pip3 install -r requirements-dev.txt`
* run `make help` for list of commands you can run
