# Data Audit

Total Rows: 97,929

## Columns
### title
- Dtype: str
- Null Count: 0 (0.00%)
- Distinct Count: 55,104
- Examples: ['Sr. HR Recruiter (NON IT)', 'Fire And Safety Officer', 'Opening For Performance Marketing - Chennai', 'Medical Billing Executive', 'Senior Group Product Manager -  CNS Therapy']

### jobId
- Dtype: int64
- Null Count: 0 (0.00%)
- Distinct Count: 97,679
- Examples: [270925008041, 270925007584, 270925007492, 270925007443, 270925007430]

### currency
- Dtype: str
- Null Count: 0 (0.00%)
- Distinct Count: 2
- Examples: ['INR', 'USD']

### jobUploaded
- Dtype: str
- Null Count: 0 (0.00%)
- Distinct Count: 30
- Examples: ['6 Days Ago', 'Few Hours Ago', 'Just Now', '3 Days Ago', '4 Days Ago']

### companyName
- Dtype: str
- Null Count: 4 (0.00%)
- Distinct Count: 18,668
- Examples: ['Orion', 'Apollo Hospitals International Limited, Ahmedabad', 'TVS Credit Services Ltd', 'GNR Global Services', 'Cadila Pharmaceuticals']

### tagsAndSkills
- Dtype: str
- Null Count: 571 (0.58%)
- Distinct Count: 84,307
- Examples: ['Communication,Manpower,Staffing,Convincing Power,Hiring,Recruitment,SR,Communication skills', 'Safety Officer Activities,Fire Protection,Fire Safety,Fire Engineering,Fire Prevention,Safety Management,Fire Management,Hazard Analysis', 'Performance Marketing,User Acquisition,growth marketing,Paid Marketing,Acquisition,Performance,Usage,Marketing', 'Fluent English,Spoken English,Good English Communication,Medical,Medical billing,Billing,Fluent,English', 'Product Marketing,CNS,Product Management,Nephrology,Group Product Management,Brand Marketing,Neurology,Brand Management']

### experience
- Dtype: str
- Null Count: 2,105 (2.15%)
- Distinct Count: 287
- Examples: ['2-4 Yrs', '6-11 Yrs', '12-18 Yrs', '0-3 Yrs', '5-10 Yrs']

### salary
- Dtype: str
- Null Count: 0 (0.00%)
- Distinct Count: 1,339
- Examples: ['2-4 Lacs PA', '3-5 Lacs PA', 'Not disclosed', '70,000-2 Lacs PA', '8-18 Lacs PA']

### location
- Dtype: str
- Null Count: 0 (0.00%)
- Distinct Count: 10,066
- Examples: ['Kolkata(Chinar Park)', 'Gandhinagar, Ahmedabad', 'Chennai', 'Mohali, Chandigarh, Kharar, Zirakpur', 'Ahmedabad']

### companyId
- Dtype: int64
- Null Count: 0 (0.00%)
- Distinct Count: 18,328
- Examples: [645563, 14072, 1324750, 123804403, 14957]

### ReviewsCount
- Dtype: float64
- Null Count: 35,252 (36.00%)
- Distinct Count: 1,375
- Examples: [5162.0, 2892.0, 2134.0, 571.0, 462.0]

### AggregateRating
- Dtype: float64
- Null Count: 35,252 (36.00%)
- Distinct Count: 41
- Examples: [4.0, 4.2, 3.4, 3.7, 4.1]

### jobDescription
- Dtype: str
- Null Count: 0 (0.00%)
- Distinct Count: 80,679
- Examples: ['Preferred candidate profile . .', 'Ensure active Fire Protection System,such as Fire Hydrant system,Fire extinguishers,Fire Alarm smoke detector system,Sprinkler system keep in good condition', 'MBA Marketing (preferred Tier II or III B- School). <br><br>Experience <br><br> 12+ years exp in Digital Marketing with a focus on performance marketing/ content strategy / campaign management along with team handling experience<br><br>Mobility Experience / development of mobile sites / Apps', 'Job Title-Medical Billing Executive\nLocation-Mohali\nSalary-20-22k ctc\n\nBenefits:\nCab facility\nIncentives\nOne time meal\n\nQualification-12 passed +6 months experience/graduate/postgraduate\nGood communication skills\nevening shift\n\nCall at 6239334478', 'Principal Tasks & Responsibilities : (Please write all the major jobs that the employee is required to carry out )<br><br>Making visual aid and cycle wise and promotional inputs as per brand requirement']

### minimumSalary
- Dtype: float64
- Null Count: 571 (0.58%)
- Distinct Count: 164
- Examples: [200000.0, 300000.0, 0.0, 70000.0, 800000.0]

### maximumSalary
- Dtype: float64
- Null Count: 571 (0.58%)
- Distinct Count: 204
- Examples: [400000.0, 500000.0, 0.0, 200000.0, 1800000.0]

### minimumExperience
- Dtype: float64
- Null Count: 571 (0.58%)
- Distinct Count: 31
- Examples: [2.0, 6.0, 12.0, 0.0, 5.0]

### maximumExperience
- Dtype: float64
- Null Count: 571 (0.58%)
- Distinct Count: 33
- Examples: [4.0, 11.0, 18.0, 3.0, 10.0]

## Skills
- Rows with empty/null skills: 571
- Distinct raw tokens: 59,479
- Tokens exported (count >= 5): 14,843 covering 91.3% of mentions

## Baskets Audit: 34,569 vs 30,134

The original project plan stated 30,134 baskets, whereas data-v3 produced 34,569 baskets. The difference arose from how tech postings were filtered and cleaned across project stages.

In the initial exploratory plan, a draft filter selected 33,724 postings based on skill tags. After dropping exact duplicates and empty skill lists, 30,134 rows survived. The plan assumed mining baskets would match that preliminary count of 30,134 postings (comprising 13,185 generic software engineer rows, 4,086 unmatched rows, and 12,863 role-labelled rows).

In the pipeline implementation in `etl/clean.py`, the tech filter checked 32 keywords from `etl/tech_terms.txt` across both `title` and `tagsAndSkills` columns of `data/raw/indian-job-market-dataset-2025.xlsx`. This broader check identified 38,271 candidate tech postings. Cleaning dropped 100 exact duplicates, 80 rows with no skills after splitting, and 3,522 reposts, leaving 34,569 rows saved to `data/clean.parquet`.

In `etl/label.py`, the `build_baskets` function created one basket per row of `data/clean.parquet`, saving 34,569 records to `data/baskets.parquet`. In that file, 32,949 baskets contain one or more canonical skill IDs and 1,620 contain empty lists after mapping against `artifacts/skill_vocab.json`.
