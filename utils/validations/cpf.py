import re

from django.core.exceptions import ValidationError


def normalize_cpf(cpf):
    """Normalize a Brazilian CPF number.

    Args:
        cpf: String containing the CPF (may contain dots and dashes or not)

    Returns:
        String with the normalized CPF

    """
    return re.sub(r"\D", "", cpf)


def validate_cpf(cpf):
    """Validate a Brazilian CPF number.

    Args:
        cpf: String containing the CPF (may contain dots and dashes or not)

    Raises:
        ValidationError: If the CPF is invalid

    """
    # Remove dots and dashes
    clean_cpf = re.sub(r"\D", "", cpf)

    # Check if it has 11 digits
    if len(clean_cpf) != 11:
        raise ValidationError("CPF must have 11 digits.")

    # Check if all digits are the same (invalid CPF)
    if clean_cpf == clean_cpf[0] * 11:
        raise ValidationError("Invalid CPF.")

    # Calculate the check digits
    new_cpf = clean_cpf[:9]
    reverse = 10
    total = 0

    for i in range(19):
        if i > 8:
            i -= 9

        total += int(new_cpf[i]) * reverse

        reverse -= 1
        if reverse < 2:
            reverse = 11
            d = 11 - (total % 11)

            if d > 9:
                d = 0
            total = 0
            new_cpf += str(d)

    # Check if the calculated digits match the provided ones
    if new_cpf != clean_cpf:
        raise ValidationError("Invalid CPF.")

    return True


def format_cpf(cpf):
    """Format a CPF to the pattern XXX.XXX.XXX-XX.

    Args:
        cpf: String containing the CPF (digits only)

    Returns:
        String with the formatted CPF

    """
    clean_cpf = re.sub(r"\D", "", cpf)

    if len(clean_cpf) != 11:
        return cpf

    return f"{clean_cpf[:3]}.{clean_cpf[3:6]}.{clean_cpf[6:9]}-{clean_cpf[9:]}"
