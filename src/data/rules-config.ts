export const ruleTokenGenerators = [
  {
    value: 'UUID',
    title: 'Generic - VGS Alias (Default)',
  },
  {
    value: 'NUM_LENGTH_PRESERVING',
    title: 'Generic - Numeric Length Preserving',
  },
  {
    value: 'FPE_SIX_T_FOUR',
    title: 'Payment Card - Format Preserving, Luhn Valid (6T4)',
  },
  {
    value: 'FPE_T_FOUR',
    title: 'Payment Card - Format Preserving, Luhn Valid (T4)',
  },
  {
    value: 'PFPT',
    title: 'Payment Card - Prefixed, Luhn Valid, 19 Digits Fixed Length',
  },
  {
    value: 'NON_LUHN_FPE_ALPHANUMERIC',
    title: 'Payment Card - Format Preserving - Non Luhn Valid',
  },
  // {
  //   value: 'FPE_SSN_T_FOUR',
  //   title: 'SSN - Format Preserving (A4)',
  // },
  // {
  //   value: 'FPE_ACC_NUM_T_FOUR',
  //   title: 'Account Number - Numeric Length Preserving (A4)',
  // },
  // {
  //   value: 'FPE_ALPHANUMERIC_ACC_NUM_T_FOUR',
  //   title: 'Account Number - Alphanumeric Length Preserving (A4)',
  // },
  // {
  //   value: 'GENERIC_T_FOUR',
  //   title: 'Generic - VGS Alias Last Four (T4)',
  // },
  {
    value: 'RAW_UUID',
    title: 'Generic - UUID',
  },
];

export const operationsMappings: any = {
  REDACT: 'Redact',
  ENRICH: 'Reveal',
};
