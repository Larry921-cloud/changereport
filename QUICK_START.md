# Quick Start Guide

## 🚀 Get Started in 3 Steps

### 1. Start the Server
The server is already running! If you need to restart it:
```bash
cd "\\wsl.localhost\Ubuntu\home\laurencesher\projects\changereport"
npm start
```

### 2. Open the Application
Open your web browser and navigate to:
```
http://localhost:3000
```

### 3. Upload Your Change Data
1. Click the upload area or drag & drop your Excel file
2. Supported formats: `.xls`, `.xlsx`, `.txt` (Unicode Text)
3. Click "Upload & Analyze"
4. Wait for the analysis to complete
5. Click "📊 Generate Interactive Report"

## 📊 Using the Interactive Report

### Available Features
- **Filter by Category**: Dropdown menu to select specific change categories
- **Filter by Date Range**: Set start and end dates for analysis
- **Real-time Updates**: All charts and tables update instantly when filters are applied
- **Export to CSV**: Download filtered data for further analysis
- **Multiple Visualizations**:
  - Changes by Category (Doughnut Chart)
  - Changes by Type (Pie Chart)
  - Changes Timeline (Line Chart)
  - Top 10 Systems (Horizontal Bar Chart)
  - Impact Distribution (Bar Chart)

### Sharing Reports
The report page is fully self-contained and can be shared:

**Option 1: Save and Email**
1. On the report page, press `Ctrl+S` (or `Cmd+S` on Mac)
2. Save as "Webpage, Complete"
3. Share the HTML file via email or shared drive

**Option 2: Print to PDF**
1. On the report page, press `Ctrl+P` (or `Cmd+P` on Mac)
2. Select "Save as PDF" as the destination
3. Share the PDF

**Note**: The report maintains full interactivity when saved as HTML, but loses filtering capabilities when converted to PDF.

## 💡 Tips

### Data Format
Your Excel file should have these column headers (case-insensitive):
- ID
- Assignee
- Customer Name
- Subject
- Reason / Benefit of Change
- Type of Change
- CM: Category
- Start Date (format: DD-MM-YY)
- Start Time (HH:MM)
- End Date (format: DD-MM-YY)
- End Time (HH:MM)
- Name of System / Application worked or config applied on?
- Impact Description
- Regions Affected
- Pre-checks / Activities
- MOP
- Rollback Plan
- Post Change Testing
- Standard Change List

### Troubleshooting

**Server won't start?**
- Make sure port 3000 is not already in use
- Try running: `npm install` to reinstall dependencies

**Upload fails?**
- Check that your file is a valid Excel format
- Ensure file size is under 10MB
- Verify column headers match the expected format

**Report shows "No Data"?**
- Make sure you clicked "Generate Interactive Report" after upload
- Don't close the upload page before opening the report
- Try refreshing and re-uploading

**Charts not displaying?**
- Check your internet connection (Chart.js loads from CDN)
- Ensure JavaScript is enabled in your browser
- Try a different browser

## 🎯 Example Workflow

1. **Monday Morning**: Upload last week's change records
2. **Review Summary**: Check total changes, categories, and systems affected
3. **Generate Report**: Click "Generate Interactive Report"
4. **Filter by Category**: Select "Radio Network" to see network-specific changes
5. **Analyze Timeline**: Identify peak change periods
6. **Export Data**: Download CSV for detailed offline analysis
7. **Share with Team**: Save report as HTML and email to stakeholders
8. **Monthly Review**: Compare reports month-over-month for trends

## 🔒 Data Privacy

- All data processing happens locally on your machine
- No data is sent to external servers
- Reports are generated client-side in your browser
- You have full control over data sharing

## 📞 Need Help?

- Review the full README.md for detailed documentation
- Check the server console for error messages
- Verify your Excel file format matches requirements

---

**Current Status**: ✅ Server running at http://localhost:3000

Ready to analyze your change data!
