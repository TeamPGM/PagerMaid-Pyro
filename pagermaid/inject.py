import inspect
import pagermaid.enums as enums
import pagermaid.services as services
from typing import Dict, Optional


def inject(message: enums.Message, function, **data) -> Optional[Dict]:
    try:
        signature = inspect.signature(function)
    except Exception:
        return None
    for parameter_name, parameter in signature.parameters.items():
        class_name = parameter.annotation.__name__
        param = message if class_name == "Message" else services.get(class_name)
        if not param:
            if parameter_name == "message":
                param = message
            else:
                param = services.get(parameter_name.capitalize())
        data.setdefault(parameter_name, param)
    return data
