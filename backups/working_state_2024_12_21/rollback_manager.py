class RollbackManager:
    def __init__(self, db=None):
        self.operations = []
        self.db = db

    def add_operation(self, operation, rollback_operation):
        self.operations.append((operation, rollback_operation))

    def execute(self):
        executed_operations = []
        try:
            for operation, _ in self.operations:
                operation()
                executed_operations.append(operation)
        except Exception as e:
            for operation, rollback_operation in reversed(self.operations[:len(executed_operations)]):
                try:
                    rollback_operation()
                except Exception as rollback_error:
                    print(f"Error during rollback: {str(rollback_error)}")
            raise e

    def clear(self):
        self.operations = []
