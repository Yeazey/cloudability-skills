# CSA ROI Assessment PowerPoint Generator

Automated tool to generate CSA ROI Assessment PowerPoint presentations from Excel files.

## 📁 Required Files

This folder must contain:
1. **generate_csa_deck.py** - The generator script
2. **CSA ROI Assessment Template.pptx** - The PowerPoint template (with zeroed data)

## 🚀 Usage

### Basic Command
```bash
python3 generate_csa_deck.py <path_to_excel_file>
```

### Example
```bash
python3 generate_csa_deck.py "/Users/username/Desktop/Merck Sharp & Dohme LLC - 156565687398 - 2026-05 - CSASA-246 - No Upfront - v2026-06-25 15-35-20.xlsx"
```

## 📊 What It Does

The script will:
1. **Read** the Excel file's "Executive Summary" tab
2. **Extract** all required metrics using label-based search (works across different Excel structures)
3. **Generate** a new PowerPoint with the customer's name automatically extracted from the filename
4. **Save** the output in the same directory as the input Excel file

### Output Filename Format
`[Customer Name] CSA ROI Assessment.pptx`

Example: `Merck Sharp & Dohme LLC CSA ROI Assessment.pptx`

## 📋 What Gets Populated

### Slide 1
- Customer name (replaces `[Customer Name]` placeholder)

### Slide 9 (Font: 11pt)
**Current Metrics:**
- EDP (On-demand usage)
- Current Coverage
- Flexibility (As-Is)
- Current Savings

**Projected Metrics (m12):**
- EDP
- Coverage (Projected Net Effective Discount)
- Flexibility (CSA at month 12)
- Projected Savings (Cloudwiry)

**Hourly Cost Pattern:**
- Stable %
- Fluctuations %
- Stable OD Equivalent

### Slide 10 (Font: 8pt)
- Font size applied to all tables

### Slide 11 (Font: 11pt)
**3-Year Financial Impact:**
- Current state savings (Years 1-3)
- CSA savings (Years 1-3)
- Incremental savings (Years 1-3)
- % Increase (Years 1-3)
- Flexibility (Years 1-3)

## 🔧 Requirements

### Python Packages
```bash
pip install python-pptx pandas openpyxl
```

### Excel File Requirements
- Must have an "Executive Summary" sheet
- Must follow standard CSA format with these labels:
  - "EDP (On-demand usage)"
  - "Current Coverage"
  - "Commitment cash flow flexibility - As-Is"
  - "Commitment cash flow flexibility"
  - "Current state - savings"
  - "Cloudwiry - savings"
  - "Projected Net Effective Discount"
  - "stable", "fluctuations", "Stable OD Equivalent"
  - "Incremental", "% Increase", "Flexibility"

## ✅ Universal Mapping

The script uses **label-based search** instead of fixed row numbers, making it work across different Excel file structures. It searches for specific text labels in the Excel file, so it adapts automatically even if rows shift between different customer files.

## 🎯 Success Indicators

After running, you should see:
```
================================================================================
SUCCESS!
================================================================================

Generated: /path/to/Customer Name CSA ROI Assessment.pptx

Slide 9: Current Savings $X, Projected $Y
Slide 11: CSA Year 1 $A, Year 2 $B, Year 3 $C
```

## ⚠️ Important Notes

1. **Charts are NOT automated** - You must manually insert chart images from Excel tabs:
   - Executive Summary tab → Slide 9
   - Additional Analysis tab → Slide 10

2. **Template must be in same folder** - Keep `CSA ROI Assessment Template.pptx` in the same directory as `generate_csa_deck.py`

3. **Customer name extraction** - The script automatically extracts the customer name from the Excel filename (text before the first dash and account number)

4. **Font sizes are fixed**:
   - Slide 9: 11pt
   - Slide 10: 8pt
   - Slide 11: 11pt

## 🐛 Troubleshooting

### "Template not found" error
- Ensure `CSA ROI Assessment Template.pptx` is in the same folder as the script

### "Excel file not found" error
- Check the file path is correct
- Use quotes around paths with spaces

### Wrong data populated
- Verify the Excel file has an "Executive Summary" sheet
- Check that the Excel follows standard CSA format with expected labels

## 📞 Support

For issues or questions, contact the CSA team.

---

**Version:** 1.0  
**Last Updated:** July 2026
