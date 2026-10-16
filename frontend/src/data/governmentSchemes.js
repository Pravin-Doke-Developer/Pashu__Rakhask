export const governmentSchemeCategories = [
  { id: 'all', label: 'All Schemes' },
  { id: 'health', label: 'Animal Healthcare' },
  { id: 'livestock', label: 'Livestock & Dairy' },
  { id: 'maharashtra', label: 'Maharashtra Schemes' },
  { id: 'financial', label: 'Farmer Financial Support' },
];

const centralCatalogue =
  'https://www.dahd.gov.in/index.php/en/schemes-programmes';

export const governmentSchemes = [
  {
    id: 'lhdcp',
    name: 'Livestock Health and Disease Control Programme (LHDCP)',
    description:
      'A central programme supporting livestock health and control of animal diseases through prevention, surveillance, and veterinary services.',
    category: 'health',
    governmentLevel: 'Central Government',
    department: 'Department of Animal Husbandry and Dairying, Government of India',
    beneficiaries: 'Livestock owners and animal-health services.',
    supportType: 'Animal healthcare and disease control',
    officialUrl: 'https://www.dahd.gov.in/en/schemes-programmes/lhdcp',
    sourceUrl: centralCatalogue,
    keywords: ['vaccination', 'veterinary', 'disease prevention', 'livestock health'],
  },
  {
    id: 'nadcp',
    name: 'National Animal Disease Control Programme (NADCP)',
    description:
      'A central programme focused on controlling Foot and Mouth Disease and brucellosis in livestock.',
    category: 'health',
    governmentLevel: 'Central Government',
    department: 'Department of Animal Husbandry and Dairying, Government of India',
    beneficiaries: 'Cattle, buffalo, sheep, goats, pigs, and their keepers.',
    supportType: 'Animal disease control',
    officialUrl: centralCatalogue,
    sourceUrl: centralCatalogue,
    keywords: ['FMD', 'foot and mouth disease', 'brucellosis', 'vaccination'],
  },
  {
    id: 'rgm',
    name: 'Rashtriya Gokul Mission (RGM)',
    description:
      'A central initiative for development and conservation of indigenous bovine breeds and improvement of bovine productivity.',
    category: 'livestock',
    governmentLevel: 'Central Government',
    department: 'Department of Animal Husbandry and Dairying, Government of India',
    beneficiaries: 'Bovine owners, breeders, and organisations involved in breed improvement.',
    supportType: 'Indigenous breed development',
    officialUrl: centralCatalogue,
    sourceUrl: centralCatalogue,
    keywords: ['cattle', 'indigenous breeds', 'breed improvement', 'dairy'],
  },
  {
    id: 'nlm',
    name: 'National Livestock Mission (NLM)',
    description:
      'A central mission supporting sustainable development of the livestock sector, including entrepreneurship and feed and fodder development.',
    category: 'livestock',
    governmentLevel: 'Central Government',
    department: 'Department of Animal Husbandry and Dairying, Government of India',
    beneficiaries: 'Livestock entrepreneurs, farmers, and organisations in eligible activities.',
    supportType: 'Livestock development and entrepreneurship',
    officialUrl:
      'https://www.dahd.gov.in/en/schemes/programmes/national_livestock_mission',
    sourceUrl: centralCatalogue,
    keywords: ['livestock', 'entrepreneurship', 'fodder', 'sheep', 'goat', 'poultry'],
  },
  {
    id: 'npdd',
    name: 'National Programme for Dairy Development (NPDD)',
    description:
      'A central programme to support the dairy sector, including organised milk procurement, processing, and related infrastructure.',
    category: 'livestock',
    governmentLevel: 'Central Government',
    department: 'Department of Animal Husbandry and Dairying, Government of India',
    beneficiaries: 'Dairy cooperatives, milk producer institutions, and dairy value-chain participants.',
    supportType: 'Dairy development and infrastructure',
    officialUrl: centralCatalogue,
    sourceUrl: centralCatalogue,
    keywords: ['milk', 'dairy', 'procurement', 'processing', 'cooperative'],
  },
  {
    id: 'ahidf',
    name: 'Animal Husbandry Infrastructure Development Fund (AHIDF)',
    description:
      'A central fund supporting eligible investment in animal husbandry infrastructure and value-chain projects.',
    category: 'livestock',
    governmentLevel: 'Central Government',
    department: 'Department of Animal Husbandry and Dairying, Government of India',
    beneficiaries: 'Eligible entrepreneurs, companies, FPOs, MSMEs, and other entities under current guidelines.',
    supportType: 'Animal husbandry infrastructure',
    officialUrl: centralCatalogue,
    sourceUrl: centralCatalogue,
    keywords: ['investment', 'infrastructure', 'dairy', 'meat processing', 'value chain'],
  },
  {
    id: 'kcc-animal-husbandry',
    name: 'Kisan Credit Card (KCC) for Animal Husbandry and Dairy',
    description:
      'The KCC facility can provide working-capital credit for eligible animal husbandry and dairy activities, subject to current rules.',
    category: 'financial',
    governmentLevel: 'Central Government',
    department: 'Government of India; credit is provided through participating financial institutions.',
    beneficiaries: 'Eligible animal husbandry and dairy farmers.',
    supportType: 'Agricultural and livestock credit',
    officialUrl: centralCatalogue,
    sourceUrl: centralCatalogue,
    keywords: ['credit', 'loan', 'working capital', 'dairy farmer', 'livestock farmer'],
  },
  {
    id: 'maharashtra-animal-husbandry-catalogue',
    name: 'Maharashtra Animal Husbandry Scheme Catalogue',
    description:
      'The Maharashtra Department of Animal Husbandry and Dairying catalogue is the official starting point for state and district-level livestock schemes.',
    category: 'maharashtra',
    governmentLevel: 'Maharashtra Government',
    department: 'Department of Animal Husbandry and Dairying, Government of Maharashtra',
    beneficiaries: 'Farmers and livestock owners; details depend on the individual scheme.',
    supportType: 'State livestock and animal welfare schemes',
    officialUrl: 'https://dahd.maharashtra.gov.in/en/schemes-programmes/',
    sourceUrl: 'https://dahd.maharashtra.gov.in/en/schemes-programmes/',
    keywords: [
      'district',
      'animal welfare',
      'livestock',
      'dairy',
      'animal health',
    ],
  },
  {
    id: 'pm-kisan',
    name: 'PM-KISAN Samman Nidhi',
    description:
      'A central income-support scheme for eligible landholding farmer families. It is general farmer support, not an animal-health scheme.',
    category: 'financial',
    governmentLevel: 'Central Government',
    department: 'Department of Agriculture and Farmers Welfare, Government of India',
    beneficiaries: 'Farmer families who meet the scheme guidelines.',
    supportType: 'Farmer income support',
    officialUrl: 'https://pmkisan.gov.in/',
    sourceUrl: 'https://pmkisan.gov.in/',
    keywords: ['income support', 'farmer', 'agriculture', 'PM Kisan'],
  },
].map((scheme) => ({
  ...scheme,
  eligibilityNote:
    'Check the official website for current eligibility, guidelines, and application availability.',
}));
