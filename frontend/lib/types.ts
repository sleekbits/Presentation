export type Placeholder = {
  key: string;
  format: string;
  slideIndex: number;
  shapeName?: string;
  context: string;
  suggestedType: 'string' | 'number' | 'date' | 'currency' | 'longtext';
};
