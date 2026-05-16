import sys
import io
import traceback

class CodeEvaluator:
    @staticmethod
    def evaluate(user_code: str, test_code: str) -> tuple[bool, str, str]:
        """
        Ejecuta el código del usuario de forma aislada e inyecta los resultados
        en el código de test para validarlos.
        """
        # 1. Redirigir el stdout (los prints del usuario) a la memoria RAM
        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()
        
        # 2. Entorno aislado (Sandbox) para que las variables no contaminen la app
        user_env = {}
        
        try:
            # Ejecutar código del estudiante
            exec(user_code, {}, user_env)
            stdout_result = redirected_output.getvalue()
            
            # 3. Ejecutar los Tests
            if test_code and test_code.strip():
                # Inyectamos el resultado del alumno en el entorno del test
                test_env = {
                    "user_stdout": stdout_result,  # Para comprobar prints
                    "user_env": user_env           # Para comprobar variables creadas
                }
                exec(test_code, {}, test_env)
            
            return True, stdout_result, "¡Excelente! Tu código ha superado todas las pruebas."
            
        except AssertionError as ae:
            # Si el test falla, capturamos el mensaje de error del assert
            stdout_result = redirected_output.getvalue()
            error_msg = str(ae) if str(ae) else "El resultado no es el esperado."
            return False, stdout_result, f"❌ Fallo de lógica: {error_msg}"
            
        except SyntaxError as se:
            # Errores de escritura (falta de paréntesis, etc.)
            stdout_result = redirected_output.getvalue()
            return False, stdout_result, f"❌ Error de Sintaxis (línea {se.lineno}): {se.msg}"
            
        except Exception as e:
            # Cualquier otro error (ZeroDivisionError, TypeError...)
            stdout_result = redirected_output.getvalue()
            error_type = type(e).__name__
            error_msg = str(e)
            return False, stdout_result, f"❌ {error_type}: {error_msg}"
            
        finally:
            # CRÍTICO: Restaurar la salida estándar siempre. Si esto falla,
            # Streamlit dejará de imprimir en la terminal de tu servidor.
            sys.stdout = old_stdout