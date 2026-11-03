# Day 4: Area-Based Transaction Analysis

## Objective
Compare areas using transaction counts and median price per sqm.

## Dataset Overview
- Total source records: 134,185
- Records eligible for area analysis: 134,185
- Distinct areas analyzed: 253

## Top 10 Areas by Transaction Count
                     AREA_EN  transaction_count median_price_per_sqm  valid_price_records
           Madinat Al Mataar              12775            18,178.99                12775
     JUMEIRAH VILLAGE CIRCLE               8602            15,750.42                 8602
DUBAI LAND RESIDENCE COMPLEX               5219            15,347.33                 5219
                BUSINESS BAY               5152            25,960.47                 5152
                       MAJAN               4424            15,459.83                 4424
               Al Yelayiss 1               3927            19,611.11                 3927
             Al Hebiah Fifth               3215            18,521.86                 3215
                  Palm Deira               3198            30,390.08                 3198
             Jabal Ali First               2908            17,482.22                 2908
                       ARJAN               2844            17,030.31                 2844

## Top 10 Areas by Median Price per Sqm
            AREA_EN  transaction_count median_price_per_sqm  valid_price_records
    Jumeirah Second                 57            96,884.57                   57
    Um Suqaim First                 39            64,583.45                   39
         BLUEWATERS                 60            55,369.03                   60
Trade Center Second                141            51,899.57                  141
        Marsa Dubai                358            47,691.31                  358
      Palm Jumeirah                 30            45,252.64                   30
       TECOM SITE A                726            43,708.26                  726
 Trade Center First                143            39,843.21                  143
     Jumeirah First                105            38,871.05                  105
      BUSINESS PARK               1735            38,212.82                 1735

## Methodology
- Individual price per sqm = TRANS_VALUE / ACTUAL_AREA.
- Area-level price is the median of individual price-per-sqm values.
- Areas with fewer than 30 valid records are excluded from the price comparison chart.
- The 30-record threshold is an analysis choice to reduce the influence of very small samples; it is not an official source rule.
- The area summary CSV retains all eligible areas.
- Original source records are not modified.

## Limitations
- Small samples can produce unstable area comparisons.
- ACTUAL_AREA is used because it was valid and positive for all records in the earlier data-quality checks.
- Currency unit has not been independently verified.
- Transaction values do not establish rental yield or investment returns.

## Output Files
- day04_area_summary_all.csv
- day04_top_areas_by_count.png
- day04_median_price_per_sqm.png