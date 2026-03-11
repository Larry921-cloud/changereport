# ITIL 4 Change Enablement App - User Guide

## 🎯 Step-by-Step Usage Guide

### Step 1: Access the Application

1. Open your web browser (Chrome, Firefox, Edge, or Safari)
2. Navigate to: `http://localhost:3000`
3. You should see the main upload page with a purple gradient header

### Step 2: Upload Your Change Data

You have two options to upload your file:

**Option A: Click to Browse**
1. Click anywhere in the dashed upload area
2. A file browser will open
3. Select your Excel file (.xls, .xlsx, or .txt)
4. Click "Open"

**Option B: Drag & Drop**
1. Open your file explorer
2. Find your Excel change data file
3. Drag it over the upload area
4. Drop it when the area turns green

**After Selection:**
- You'll see a ✓ checkmark with your filename
- The file size will be displayed
- A "Change File" button appears if you want to select a different file
- Most importantly: **A large "🚀 Upload & Analyze" button appears below**

### Step 3: Analyze the Data

1. Click the **"🚀 Upload & Analyze"** button
2. Wait for the analysis (usually takes 2-5 seconds)
3. You'll see a success message: "Successfully analyzed X change records!"
4. The page will show:
   - Total Changes count
   - Number of Categories
   - Number of Change Types
   - Systems Affected
5. Two preview charts appear:
   - Changes by Category (doughnut chart)
   - Changes Over Time (line chart)

### Step 4: Generate the Interactive Report

1. Look for the large green button: **"📊 Generate Interactive Report"**
2. Click it
3. A new browser tab/window opens with the full report
4. The report includes:
   - Summary statistics (4 stat cards)
   - Filter section at the top
   - 5 detailed charts
   - Complete change records table
   - Key insights section

### Step 5: Use the Filters (Interactive Report)

**Filter by Category:**
1. Find the "Change Category" dropdown at the top
2. Click it to see all available categories:
   - Radio Network
   - IP Core
   - Packet Core
   - Transmission Network
   - Systems and IT
   - Software Engineering
   - Cyber Security
   - Billing and Revenue
3. Select a category (or leave as "All Categories")

**Filter by Date Range:**
1. Find "Date From" field
2. Click to open date picker
3. Select your start date
4. Find "Date To" field
5. Select your end date

**Apply Filters:**
1. Click the blue **"Apply Filters"** button
2. Watch as ALL sections update:
   - Summary stats recalculate
   - All 5 charts redraw with filtered data
   - Table shows only filtered records
   - Insights regenerate

**Reset Filters:**
- Click the gray **"Reset"** button to return to all data

### Step 6: Export Data

**Export to CSV:**
1. Scroll to the "Detailed Change Records" table
2. Click the green **"Export to CSV"** button
3. The file downloads with format: `change-report-YYYY-MM-DD.csv`
4. Open in Excel, Google Sheets, or any spreadsheet app

### Step 7: Share the Report

**Method 1: Save as HTML (Recommended)**
1. In the report page, press `Ctrl+S` (Windows) or `Cmd+S` (Mac)
2. Choose location to save
3. Select "Webpage, Complete" as file type
4. Click Save
5. The HTML file can be:
   - Emailed to stakeholders
   - Shared on network drives
   - Opened offline (keeps all interactivity!)

**Method 2: Print to PDF**
1. In the report page, press `Ctrl+P` (Windows) or `Cmd+P` (Mac)
2. Select "Save as PDF" or "Microsoft Print to PDF"
3. Adjust print settings if needed
4. Click Save
5. Note: PDF loses interactivity but is universally viewable

**Method 3: Screenshot**
- Use Windows Snipping Tool or Mac Screenshot app
- Capture specific charts or sections
- Good for quick sharing in emails or presentations

## 📊 Understanding the Report Sections

### Summary Statistics (Top Cards)
- **Total Changes**: Count of all change records in dataset
- **Categories**: Number of unique change categories
- **Systems**: Number of unique systems/applications affected
- **Date Range**: Earliest to latest change date

### Chart Visualizations

1. **Changes by Category** (Doughnut Chart)
   - Shows distribution across all categories
   - Colors are colorblind-friendly
   - Click legend items to show/hide categories

2. **Changes by Type** (Pie Chart)
   - Standard Change, CAB Change, Work Order distribution
   - Hover for exact counts

3. **Changes Timeline** (Line Chart)
   - Shows changes over time by month
   - Helps identify busy periods
   - Trend analysis

4. **Top 10 Systems** (Horizontal Bar Chart)
   - Most frequently changed systems
   - Helps identify high-maintenance systems

5. **Impact Distribution** (Bar Chart)
   - Breakdown by impact level
   - No Impact, Degradation, Unavailable, etc.

### Detailed Change Records Table
- Shows all change data in tabular format
- Columns include:
  - ID, Date, Category, Type
  - Subject, System, Impact
  - **Explanation**: AI-generated layman's summary
- Updates based on filters
- Sortable (click headers)
- Scrollable for many records

### Key Insights Section
Automatically generated insights include:
- Most active category
- Most impacted system
- Change type distribution
- Busiest period (month)

## 💡 Tips & Best Practices

### Data Preparation
- Ensure Excel file has proper column headers
- Use DD-MM-YY format for dates
- Use HH:MM format for times (24-hour)
- Remove any empty rows at the top
- Save as .xlsx for best compatibility

### Performance
- Files up to 1000 records load instantly
- Files with 1000+ records may take a few seconds
- Filtering is real-time (instant)
- Charts render very quickly

### Sharing Best Practices
- For **external stakeholders**: Share HTML file (fully interactive)
- For **executives**: Share PDF (clean, printable)
- For **data analysis**: Export CSV and share spreadsheet
- For **presentations**: Take screenshots of specific charts

### Filtering Strategies
- **Category Analysis**: Filter one category at a time to deep-dive
- **Time Period**: Filter by quarter or month for periodic reports
- **Combined Filters**: Use both category AND date for focused analysis
- **Compare**: Generate multiple reports with different filters

## 🔧 Troubleshooting

### "Upload & Analyze" Button Not Visible
- **Solution**: The button appears AFTER you select a file
- Look below the upload area after file selection
- If still not visible, refresh page and try again

### Upload Fails
- Check file format (.xls, .xlsx, or .txt)
- Ensure file isn't corrupted
- Try saving Excel file in different format
- Check file size (should be under 10MB)

### Report Opens But Shows "No Data Found"
- **Solution**: Don't close the upload page before opening report
- The report uses sessionStorage which requires the upload page to remain open
- Try: Keep upload page open, click "Generate Interactive Report" again

### Charts Not Displaying
- Check internet connection (Chart.js loads from CDN)
- Enable JavaScript in browser
- Try different browser
- Clear browser cache

### Filters Not Working
- Click "Apply Filters" button after selecting filters
- Ensure date range is valid (From date < To date)
- Try "Reset" button first, then reapply filters

### Export Button Not Working
- Check browser's download settings
- Allow downloads from localhost
- Try different browser

## 🎓 Example Workflows

### Monthly Change Review Meeting
1. Upload last month's change data
2. Generate report
3. Filter by each category, one at a time
4. Note the busiest category
5. Export CSV of busiest category for detailed review
6. Share HTML report with team before meeting

### Executive Quarterly Report
1. Upload entire quarter's data
2. Generate report
3. Take screenshots of key charts
4. Note top 3 insights from Insights section
5. Export to PDF for distribution
6. Present filtered views by category during meeting

### System-Specific Analysis
1. Upload all change data
2. Generate report
3. Look at "Top 10 Systems" chart
4. Manually filter table (scroll to find specific system)
5. Export filtered CSV for that system
6. Share with system owner

### Year-End Analysis
1. Upload full year of data
2. Generate report
3. Note overall statistics
4. Filter by quarters (Jan-Mar, Apr-Jun, etc.)
5. Compare quarterly trends
6. Identify seasonal patterns

## 📞 Getting Help

If you encounter issues:
1. Check this User Guide first
2. Review the README.md for technical details
3. Check the browser console (F12) for error messages
4. Verify your data format matches requirements
5. Try with a smaller sample file first

## 🚀 Advanced Features

### Keyboard Shortcuts
- `Ctrl+S` / `Cmd+S`: Save report as HTML
- `Ctrl+P` / `Cmd+P`: Print report
- `F5`: Refresh page
- `F12`: Open developer console (for debugging)

### Browser Recommendations
- **Best**: Chrome or Edge (Chromium-based)
- **Good**: Firefox, Safari
- **Minimum**: Any modern browser with JavaScript enabled

### Multiple Reports
- You can keep multiple report tabs open
- Each report is independent
- Compare different filtered views side-by-side
- Each has its own copy of the data

---

**Ready to analyze your change data!** 📊

Start at: `http://localhost:3000`
