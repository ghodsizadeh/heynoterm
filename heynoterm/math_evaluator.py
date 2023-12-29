import math


class MathBlockEvaluator:
    def __init__(self):
        # Create a dictionary to store variables
        self.variables = {}
        self.results = []

    def evaluate_expression(self, expression: str):
        if not expression.strip():
            return ""
        # Allow only safe math operations, no built-in functions
        allowed_names = {
            name: obj for name, obj in vars(math).items() if not name.startswith("__")
        }
        # Add our variable storage to the allowed names
        allowed_names.update(self.variables)

        try:
            # Compile the expression to ast, then execute it safely
            code = compile(expression.strip(), "<string>", "eval")
            return eval(code, {"__builtins__": {}}, allowed_names)
        except Exception:
            # Handle malformed expressions and other exceptions
            return ""

    def process_line(self, line):
        # Check if the line is an assignment
        if "=" in line:
            # Split on the first '=' to handle the variable assignment
            var_name, expr = line.split("=", 1)
            # Strip spaces from the variable name
            var_name = var_name.strip()
            # Save the result of the expression to the variable
            self.variables[var_name] = self.evaluate_expression(expr.strip())
            return self.variables[var_name]
        else:
            # If it's not an assignment, evaluate it as a regular expression
            return self.evaluate_expression(line.strip())

    def process_block(self, block_text):
        # Split the block text by lines and process each line
        lines = block_text.split("\n")
        results = []
        for line in lines:
            result = self.process_line(line)
            results.append(result)
        self.results = results
        return results


# Example usage
if __name__ == "__main__":
    evaluator = MathBlockEvaluator()
    block_text = """
    radius = 5


    volume = radius**2 * 3.14

    area = 3.14 * radius**2
    perimeter = 2 * 3.14 * radius
    23
    """
    results = evaluator.process_block(block_text)
    for result in results:
        print(result)
