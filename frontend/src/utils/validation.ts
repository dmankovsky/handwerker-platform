export const validationRules = {
  email: {
    required: 'Email is required',
    pattern: {
      value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
      message: 'Invalid email address',
    },
  },
  password: {
    required: 'Password is required',
    minLength: {
      value: 6,
      message: 'Password must be at least 6 characters',
    },
  },
  phone: {
    required: 'Phone number is required',
    pattern: {
      value: /^[+]?[(]?[0-9]{1,4}[)]?[-\s.]?[(]?[0-9]{1,4}[)]?[-\s.]?[0-9]{1,9}$/,
      message: 'Invalid phone number',
    },
  },
  required: (fieldName: string) => ({
    required: `${fieldName} is required`,
  }),
  minLength: (fieldName: string, length: number) => ({
    required: `${fieldName} is required`,
    minLength: {
      value: length,
      message: `${fieldName} must be at least ${length} characters`,
    },
  }),
  maxLength: (fieldName: string, length: number) => ({
    maxLength: {
      value: length,
      message: `${fieldName} must be no more than ${length} characters`,
    },
  }),
  number: (fieldName: string, min?: number, max?: number) => ({
    required: `${fieldName} is required`,
    valueAsNumber: true,
    validate: (value: number) => {
      if (min !== undefined && value < min) {
        return `${fieldName} must be at least ${min}`;
      }
      if (max !== undefined && value > max) {
        return `${fieldName} must be no more than ${max}`;
      }
      return true;
    },
  }),
};

export const confirmPassword = (password: string) => ({
  validate: (value: string) => value === password || 'Passwords do not match',
});
