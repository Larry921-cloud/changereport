# ITIL 4 Change Enablement Web Application

A comprehensive web-based application for analyzing ITIL 4 change management data. Upload Excel spreadsheets containing change records and generate interactive reports with insights and visualizations.

## Features

### 🚀 Core Functionality
- **File Upload**: Support for XLS, XLSX, and Unicode Text files
- **Automated Analysis**: AI-powered change analysis with layman's explanations
- **Interactive Dashboard**: Real-time filtering and data exploration
- **Visual Analytics**: Multiple chart types (doughnut, bar, line, pie)
- **Shareable Reports**: Generate standalone HTML reports for external sharing
- **Data Export**: Export filtered data to CSV format

### 📊 Analytics & Insights
- Changes by Category breakdown
- Changes by Type distribution
- Timeline visualization
- Top 10 Systems affected
- Impact distribution analysis
- Automated key insights generation

### 🔍 Filtering Capabilities
- Filter by Change Category
- Filter by Date Range (From/To)
- Real-time chart and table updates
- Reset filters functionality

### 📱 Responsive Design
- Mobile-friendly interface
- Print-optimized layout
- Accessibility considerations

## Installation

### Prerequisites
- Node.js (v14 or higher)
- npm (comes with Node.js)

### Setup Steps

1. Navigate to the project directory:
```bash
cd /path/to/changereport
```

2. Install dependencies:
```bash
npm install
```

3. Start the server:
```bash
npm start
```

4. Open your browser and navigate to:
```
http://localhost:3000
```

### Development Mode

For auto-restart on file changes:
```bash
npm run dev
```

## Usage

### 1. Upload Change Data

1. Click the upload area or drag and drop your Excel file
2. Supported formats:
   - `.xls` (Excel 97-2003)
   - `.xlsx` (Excel 2007+)
   - `.txt` (Unicode Text export from Excel)
3. Click "Upload & Analyze"

### 2. View Analysis Results

After upload, you'll see:
- Total changes count
- Number of categories
- Number of change types
- Systems affected
- Quick preview charts

### 3. Generate Interactive Report

1. Click "📊 Generate Interactive Report" button
2. A new window/tab opens with the full report
3. The report includes:
   - Summary statistics
   - Multiple visualization charts
   - Detailed change records table
   - AI-generated insights

### 4. Use Filters

In the report page:
1. **Category Filter**: Select specific change categories
2. **Date Range**: Set start and end dates
3. Click "Apply Filters" to update all charts and tables
4. Click "Reset" to clear filters

### 5. Export Data

Click "Export to CSV" button to download filtered data as a CSV file for further analysis in Excel or other tools.

## Data Format

The application expects Excel files with the following columns:

### Required Columns
- **ID**: Change request identifier
- **Assignee**: Person responsible
- **Customer Name**: Affected customer/department
- **Subject**: Brief description of the change
- **Reason / Benefit of Change**: Purpose and benefits
- **Type of Change**: Standard/CAB/Work Order
- **CM: Category**: Change category (e.g., Radio Network, IP Core)
- **Start Date**: Format: DD-MM-YY
- **Start Time (HH:MM)**: Time format: HH:MM
- **End Date**: Format: DD-MM-YY
- **End Time (HH:MM)**: Time format: HH:MM
- **Name of System / Application**: System affected
- **Impact Description**: Impact level/description
- **Regions Affected**: List of regions
- **Pre-checks / Activities**: Pre-change activities
- **MOP**: Method of procedure
- **Rollback Plan**: Rollback procedure
- **Post Change Testing**: Testing activities
- **Standard Change List**: For standard changes only

### Supported Categories
- Radio Network
- IP Core
- Packet Core
- Transmission Network
- Systems and IT
- Software Engineering
- Cyber Security
- Billing and Revenue

## AI-Powered Explanations

The application automatically generates layman's explanations for each change by analyzing:
- Change category context
- System/application affected
- Subject and purpose
- Impact description

Example output:
> "A radio network maintenance was performed on Cell Tower Management System. This change involved upgrading firmware to latest version. This change had no impact on users or services."

## Sharing Reports

The generated HTML report page is:
- **Self-contained**: All data embedded in the page
- **Offline-capable**: Can be saved and viewed without server
- **Shareable**: Can be sent via email or shared drives
- **Interactive**: Full filtering and visualization features

To share:
1. Generate the report
2. Use browser's "Save As" → "Webpage, Complete"
3. Share the HTML file

## Technology Stack

### Backend
- **Node.js**: Runtime environment
- **Express**: Web server framework
- **Multer**: File upload handling
- **XLSX**: Excel file parsing
- **CORS**: Cross-origin resource sharing

### Frontend
- **HTML5/CSS3**: Structure and styling
- **Vanilla JavaScript**: Client-side logic
- **Chart.js**: Data visualization
- **Responsive Design**: Mobile-first approach

## File Structure

```
changereport/
├── server.js              # Express server and API endpoints
├── package.json           # Dependencies and scripts
├── public/
│   ├── index.html         # Main upload page
│   ├── app.js             # Upload page logic
│   ├── styles.css         # Upload page styles
│   ├── report.html        # Interactive report page
│   ├── report.js          # Report logic with filtering
│   └── report-styles.css  # Report page styles
└── README.md              # This file
```

## API Endpoints

### POST /api/upload
Upload and analyze change data file.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: File upload (field name: `file`)

**Response:**
```json
{
  "success": true,
  "totalRecords": 216,
  "data": [...],
  "analysis": {
    "totalChanges": 216,
    "byCategory": {...},
    "byType": {...},
    "byMonth": {...},
    "byImpact": {...},
    "topSystems": {...},
    "dateRange": {...}
  }
}
```

## Browser Compatibility

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Mobile browsers: ✅ Responsive design

## Troubleshooting

### Port Already in Use
If port 3000 is already in use, modify `server.js`:
```javascript
const PORT = 3001; // Change to available port
```

### File Upload Fails
- Ensure file is valid Excel format
- Check file size (should be < 10MB)
- Verify column headers match expected format

### Charts Not Displaying
- Ensure JavaScript is enabled
- Check browser console for errors
- Verify Chart.js CDN is accessible

### No Data in Report
- Make sure to click "Generate Interactive Report" after upload
- Check that sessionStorage is enabled in browser
- Try refreshing the upload page and re-uploading

## Future Enhancements

Potential features for future versions:
- [ ] Database storage for historical analysis
- [ ] User authentication and multi-tenancy
- [ ] Advanced filtering (multiple categories, impact levels)
- [ ] PDF export functionality
- [ ] Real-time collaboration features
- [ ] Integration with ITSM tools
- [ ] Predictive analytics and trends

## License

MIT License

## Support

For issues or questions, please create an issue in the project repository.
