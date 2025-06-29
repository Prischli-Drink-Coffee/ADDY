import os
import pymysql
from src.utils.custom_logging import get_logger
from src.utils.env import Env

env = Env()
log = get_logger(__name__)


class CreateSQL:

    def __init__(self):
        self.path_to_sql = os.path.join(os.path.dirname(os.path.dirname(__file__)), f"{env.__getattr__('DB').strip()}.sql")

        db_host = env.__getattr__("DB_HOST").strip()
        db_port = int(env.__getattr__("DB_PORT"))
        db_user = env.__getattr__("DB_USER").strip()
        db_password = env.__getattr__("DB_PASSWORD").strip()

        log.debug(f"Connecting to MySQL: {db_user}@{db_host}:{db_port}")

        self.connection = pymysql.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    def read_sql(self):
        try:
            with self.connection.cursor() as cursor:
                db_name = env.__getattr__('DB').strip()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
                cursor.execute(f"USE `{db_name}`")

                with open(self.path_to_sql, "r", encoding="utf-8") as f:
                    sql_script = f.read()

                    statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]

                    for statement in statements:
                        try:
                            cursor.execute(statement)
                            log.info("Executed SQL statement: %s", statement[:100])
                        except pymysql.MySQLError as e:
                            log.warning(f"SQL Warning: {e}")

                self.connection.commit()
                log.info("Database was created and SQL script executed successfully")
        except Exception as ex:
            log.error("Error during SQL script execution", exc_info=True)
            raise
        finally:
            if hasattr(self, 'connection'):
                self.connection.close()


if __name__ == "__main__":
    create_sql = CreateSQL()
    create_sql.read_sql()