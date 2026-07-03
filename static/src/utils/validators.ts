/**
 * Validation utility functions for user data
 */

/**
 * Special characters that are not allowed in user names
 */
const FORBIDDEN_SPECIAL_CHARS = /[*(){}@#$%^&€\[\]=+\\|;:'",<>!?/~`]/g;

/**
 * Validates if a string contains forbidden special characters
 * @param value - String to validate
 * @returns Array of error messages (empty if valid)
 */
export function validateNoSpecialCharacters(value: string): string[] {
  const errors: string[] = [];
  
  if (!value) {
    return errors;
  }

  const foundChars = value.match(FORBIDDEN_SPECIAL_CHARS);
  
  if (foundChars) {
    const uniqueChars = [...new Set(foundChars)].join(', ');
    errors.push(` Un ou plusieurs caractères non autorisés ont été détectés : ${uniqueChars}`);
  }
  
  return errors;
}

/**
 * Validates first name and last name
 * @param firstName - First name to validate
 * @param lastName - Last name to validate
 * @returns Object with error messages for each field
 */
export function validateUserNames(firstName: string, lastName: string): { first_name: string[]; last_name: string[] } {
  const errors = {
    first_name: [] as string[],
    last_name: [] as string[],
  };

  if (firstName) {
    const firstNameErrors = validateNoSpecialCharacters(firstName);
    errors.first_name = firstNameErrors.map(msg => `Prénom: ${msg}`);
  }

  if (lastName) {
    const lastNameErrors = validateNoSpecialCharacters(lastName);
    errors.last_name = lastNameErrors.map(msg => `Nom: ${msg}`);
  }

  return errors;
}

export default {
  validateNoSpecialCharacters,
  validateUserNames,
};
