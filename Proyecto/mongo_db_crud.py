from bson.json_util import dumps, ObjectId
import json
import pymongo as mongo
from logging_base import loge

class Mongodb:

    """
        Herramientas CRUD para aplicar con MongoBD
            
            connection_string: Coloque el texto para conectar con el cluster.
                Si no coloca el texto la mongo usará un texto colocado anteriormente.
    """
    _connection_string=None
    _client=None
    _db=None
    
    def __init__(self,connection_string=None):
        try:
            if connection_string == None:
                loge.debug(f"Dirección de conexión omitida")
                pass
            else:
                self._connection_string=connection_string 
                loge.debug(f"Dirección de conexión dada")
        
        except Exception as e:

           return loge.error(f"Error: {e}")

    @classmethod    
    def set_db(self,name_db):
        """
            Crea conexión con el cluster de Mongodb y señala la db a la que se quiere conectar.

                Si no existe la db se creará automaticamente.
        """
        try:
            self._client= mongo.MongoClient(self._connection_string)
            self._db=self._client[name_db]
            loge.debug(f"Conectado a cluster con los DBs: ({self._client.database_names()}), DB fijado: ({name_db})")
            return self._db

        except Exception as e:

           return loge.error(f"Error: {e}")

    @classmethod
    def Insert_data(self,collection_name:str, json):
        """
            Crea una coleccion si esta no existe y agrega los datos en formato Json.

                Collection_name: Nombre de la base de datos.

                Json: Dato en formato Json para ingresar a la db. 
        """
        try:

            return self._db[collection_name].insert_one(json)
        
        except Exception as e:

           return loge.error(f"Error: {e}")

    @classmethod
    def update_by_id(self,collection_name,_id,update_tag,set):
        """
            Actualiza un apartado del doc.

                Collection_name: Nombre de la base de datos.

                _id: coloque el _id del doc.

                update_tag: coloque la key del dato que desea actualizar. Si no existe en el doc, se crea.

                set: coloque el nuevo dato.
        """
        try:

            return loge.debug( f"""Datos actualizados: {self._db[collection_name].update_one(
                {'_id':ObjectId(_id)},
                {"$set":{
                    update_tag:set
                }} ).modified_count}, tag: {update_tag}""")          
        
        except Exception as e:

           return loge.error(f"Error: {e}")

if __name__ == "__main__":

    db=Mongodb("mongodb://localhost:27017/").set_db("joan33")
    #db.create_collection("joan33")
    #Mongodb().Insert_data("coll",{"joan":"blanco"})
    Mongodb().update_by_id("coll","624cd81b376a72e60ac7bfe6","man","yes")
    