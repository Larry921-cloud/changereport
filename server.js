const path = require('path');
const fs = require('fs');
require('dotenv').config({ path: path.join(__dirname, '.env') });

const express = require('express');
const multer = require('multer');
const XLSX = require('xlsx');
const cors = require('cors');
const Anthropic = require('@anthropic-ai/sdk');

const app = express();
const PORT = process.env.PORT || 3000;

// Manual .env parsing as fallback
if (!process.env.ANTHROPIC_API_KEY) {
    try {
        const envPath = path.join(__dirname, '.env');
        const envContent = fs.readFileSync(envPath, 'utf8');
        const match = envContent.match(/ANTHROPIC_API_KEY=(.*)/);
        if (match && match[1]) {
            process.env.ANTHROPIC_API_KEY = match[1].trim();
        }
    } catch (err) {
        console.error('Error reading .env file:', err.message);
    }
}

// Debug: Log API key status
console.log('API Key loaded:', process.env.ANTHROPIC_API_KEY ? 'Yes (length: ' + process.env.ANTHROPIC_API_KEY.length + ')' : 'No');

// Initialize Anthropic client
const anthropic = new Anthropic({
    apiKey: process.env.ANTHROPIC_API_KEY,
});

// Middleware
app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ limit: '50mb', extended: true }));
app.use(express.static('public'));

// Configure multer for file uploads
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

// Column mapping based on Python constants
const HEADER_ALIASES = {
    "id": "id",
    "assignee": "assignee",
    "customer name": "customer_name",
    "subject": "subject",
    "reason / benefit of change": "reason_benefit",
    "type of change": "type_of_change",
    "cm: category": "category",
    "start date": "start_date",
    "start time (hh:mm)": "start_time",
    "end date": "end_date",
    "end time (hh:mm)": "end_time",
    "name of system / application worked or config applied on?": "system_application",
    "impact description": "impact_description",
    "regions affected ( list all separated by a comma)": "regions_affected",
    "regions affected (list all separated by a comma)": "regions_affected",
    "pre-checks / activities": "pre_checks",
    "mop - ( attach if necessary ) ps!- max 2mb allowed via this form.": "mop",
    "mop - (attach if necessary) ps!- max 2mb allowed via this form.": "mop",
    "rollback plan ( attach if necessary )": "rollback_plan",
    "rollback plan (attach if necessary)": "rollback_plan",
    "post change testing ( attach if necessary )": "post_change_testing",
    "post change testing (attach if necessary)": "post_change_testing",
    "standard change list (only for std changes)": "standard_change_list",
};

const CATEGORIES = [
    "Radio Network", "IP Core", "Packet Core",
    "Transmission Network", "Systems and IT",
    "Software Engineering", "Cyber Security",
    "Billing and Revenue"
];

// Parse date in various formats (DD-MM-YY, DD/MM/YY, Excel serial, etc.)
function parseDate(dateStr) {
    if (!dateStr) return null;

    // If it's already a Date object, return it
    if (dateStr instanceof Date) return dateStr;

    // Handle Excel serial date numbers
    if (typeof dateStr === 'number') {
        // Excel dates are days since 1900-01-01 (with known Excel bug for leap year)
        const excelEpoch = new Date(1900, 0, 1);
        const daysOffset = dateStr - 2; // Excel has a leap year bug
        return new Date(excelEpoch.getTime() + daysOffset * 24 * 60 * 60 * 1000);
    }

    const dateString = dateStr.toString().trim();

    // Try DD-MM-YY or DD-MM-YYYY format (hyphen separator)
    let parts = dateString.split('-');
    if (parts.length === 3) {
        const day = parseInt(parts[0]);
        const month = parseInt(parts[1]) - 1;
        let year = parseInt(parts[2]);
        if (year < 100) year += 2000;
        if (!isNaN(day) && !isNaN(month) && !isNaN(year)) {
            return new Date(year, month, day);
        }
    }

    // Try DD/MM/YY or DD/MM/YYYY format (slash separator)
    parts = dateString.split('/');
    if (parts.length === 3) {
        const day = parseInt(parts[0]);
        const month = parseInt(parts[1]) - 1;
        let year = parseInt(parts[2]);
        if (year < 100) year += 2000;
        if (!isNaN(day) && !isNaN(month) && !isNaN(year)) {
            return new Date(year, month, day);
        }
    }

    // Try to parse as ISO date or other standard formats
    const parsed = new Date(dateString);
    if (!isNaN(parsed.getTime())) {
        return parsed;
    }

    return null;
}

// Normalize column headers
function normalizeHeaders(row) {
    const normalized = {};
    for (const key in row) {
        const lowerKey = key.toLowerCase().trim();
        const canonicalKey = HEADER_ALIASES[lowerKey] || key;
        normalized[canonicalKey] = row[key];
    }
    return normalized;
}

// Generate layman's explanation for a change using Anthropic AI
async function generateChangeExplanation(change) {
    try {
        // Focus exclusively on the 5 key columns for targeted analysis
        const changeContext = `
Subject: ${change.subject || 'N/A'}
Reason / Benefit of Change: ${change.reason_benefit || 'N/A'}
Category: ${change.category || 'N/A'}
System / Application: ${change.system_application || 'N/A'}
MOP (Method of Procedure): ${change.mop || 'N/A'}
        `.trim();

        const message = await anthropic.messages.create({
            model: "claude-sonnet-4-20250514",
            max_tokens: 300,
            messages: [{
                role: "user",
                content: `You are explaining an ITIL change record to a non-technical audience. Based on the following change details, provide a clear, concise summary in 2-3 sentences that explains what the change was trying to achieve and why it was needed. Focus on the goal and purpose of the change, not technical implementation details. Use simple layman's terms.

Change Details:
${changeContext}

Provide only the explanation, no preamble or meta-commentary.`
            }]
        });

        return message.content[0].text.trim();

    } catch (error) {
        console.error('Error generating AI explanation:', error.message);
        // Fallback to basic explanation if AI fails
        const category = change.category || 'system';
        const subject = change.subject || 'update';
        const system = change.system_application || 'infrastructure';
        return `A ${category} change was performed on ${system}: ${subject}`;
    }
}

// Process AI explanations in batches to avoid rate limits
async function generateExplanationsInBatches(dataArray, batchSize = 5) {
    const results = [];
    const totalBatches = Math.ceil(dataArray.length / batchSize);

    console.log(`Processing ${dataArray.length} records in ${totalBatches} batches of ${batchSize}...`);

    for (let i = 0; i < dataArray.length; i += batchSize) {
        const batch = dataArray.slice(i, i + batchSize);
        const batchNumber = Math.floor(i / batchSize) + 1;

        console.log(`Processing batch ${batchNumber}/${totalBatches} (records ${i + 1}-${Math.min(i + batchSize, dataArray.length)})...`);

        // Process this batch in parallel
        const batchPromises = batch.map(row => generateChangeExplanation(row));
        const batchResults = await Promise.all(batchPromises);

        results.push(...batchResults);

        // Small delay between batches to be extra safe with rate limits
        if (i + batchSize < dataArray.length) {
            await new Promise(resolve => setTimeout(resolve, 500)); // 500ms delay between batches
        }
    }

    console.log(`Completed all ${dataArray.length} AI explanations successfully!`);
    return results;
}

// API endpoint to upload and analyze file
app.post('/api/upload', upload.single('file'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: 'No file uploaded' });
        }

        // Parse Excel file
        const workbook = XLSX.read(req.file.buffer, { type: 'buffer' });
        const sheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[sheetName];

        // Convert to JSON
        let data = XLSX.utils.sheet_to_json(worksheet, { defval: '' });

        // Normalize headers
        data = data.map(row => normalizeHeaders(row));

        // Parse dates and add metadata (without explanations yet)
        data = data.map((row, index) => {
            const startDate = parseDate(row.start_date);
            const endDate = parseDate(row.end_date);

            // Format date manually to ensure consistency
            let formattedStartDate = '';
            if (startDate) {
                const day = String(startDate.getDate()).padStart(2, '0');
                const month = String(startDate.getMonth() + 1).padStart(2, '0');
                const year = startDate.getFullYear();
                formattedStartDate = `${day}/${month}/${year}`;
            }

            return {
                ...row,
                rowIndex: index + 1,
                start_date_obj: startDate ? startDate.toISOString() : null,
                end_date_obj: endDate ? endDate.toISOString() : null,
                start_date_formatted: formattedStartDate,
                start_date_display: formattedStartDate, // Add duplicate field for clarity
            };
        });

        // Generate AI explanations using batched processing to avoid rate limits
        const explanations = await generateExplanationsInBatches(data, 5);

        // Add explanations to data
        data = data.map((row, index) => ({
            ...row,
            explanation: explanations[index]
        }));

        // Generate analysis
        const analysis = analyzeChanges(data);

        res.json({
            success: true,
            totalRecords: data.length,
            data: data,
            analysis: analysis
        });

    } catch (error) {
        console.error('Error processing file:', error);
        res.status(500).json({
            error: 'Error processing file',
            details: error.message
        });
    }
});

// Analyze changes and generate insights
function analyzeChanges(data) {
    const analysis = {
        totalChanges: data.length,
        byCategory: {},
        byType: {},
        byMonth: {},
        byImpact: {},
        topSystems: {},
        dateRange: { earliest: null, latest: null }
    };

    data.forEach(change => {
        // Category breakdown
        const category = change.category || 'Unknown';
        analysis.byCategory[category] = (analysis.byCategory[category] || 0) + 1;

        // Type breakdown
        const type = change.type_of_change || 'Unknown';
        analysis.byType[type] = (analysis.byType[type] || 0) + 1;

        // Impact breakdown
        const impact = change.impact_description || 'Unknown';
        analysis.byImpact[impact] = (analysis.byImpact[impact] || 0) + 1;

        // System breakdown
        const system = change.system_application || 'Unknown';
        analysis.topSystems[system] = (analysis.topSystems[system] || 0) + 1;

        // Date range
        if (change.start_date_obj) {
            const dateObj = new Date(change.start_date_obj);
            if (!analysis.dateRange.earliest || dateObj < analysis.dateRange.earliest) {
                analysis.dateRange.earliest = dateObj;
            }
            if (!analysis.dateRange.latest || dateObj > analysis.dateRange.latest) {
                analysis.dateRange.latest = dateObj;
            }

            // Monthly breakdown
            const monthYear = dateObj.toLocaleDateString('en-GB', {
                year: 'numeric',
                month: 'short'
            });
            analysis.byMonth[monthYear] = (analysis.byMonth[monthYear] || 0) + 1;
        }
    });

    // Sort top systems
    analysis.topSystems = Object.entries(analysis.topSystems)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10)
        .reduce((obj, [key, val]) => { obj[key] = val; return obj; }, {});

    return analysis;
}

// PDF Export endpoint
app.post('/api/export-pdf', async (req, res) => {
    try {
        const PDFDocument = require('pdfkit');
        const { data, filters, password } = req.body;

        console.log(`PDF export requested for ${data ? data.length : 0} records`);

        if (!data || !Array.isArray(data)) {
            console.error('Invalid data provided to PDF export');
            return res.status(400).json({ error: 'Invalid data provided' });
        }

        // Validate password is provided
        if (!password || password.trim().length === 0) {
            return res.status(400).json({ error: 'Password is required for PDF export' });
        }

        // Create PDF document with password protection
        const doc = new PDFDocument({
            margin: 50,
            size: 'A4',
            userPassword: password,  // Password required to open/view PDF
            ownerPassword: password + '_owner',  // Password for editing (stronger)
            permissions: {
                printing: 'highResolution',  // Allow printing
                modifying: false,  // Prevent modifications
                copying: false,  // Prevent copying text
                annotating: false,  // Prevent annotations
                fillingForms: false,  // Prevent form filling
                contentAccessibility: true,  // Allow screen readers
                documentAssembly: false  // Prevent page assembly
            }
        });

        // Set response headers
        res.setHeader('Content-Type', 'application/pdf');
        res.setHeader('Content-Disposition', `attachment; filename=change-report-${new Date().toISOString().split('T')[0]}.pdf`);

        // Pipe PDF to response
        doc.pipe(res);

        // Add Rain logo on top left if available
        const logoPath = path.join(__dirname, 'assets', 'rain-logo.png');
        if (fs.existsSync(logoPath)) {
            try {
                doc.image(logoPath, 50, 50, { width: 100 });
            } catch (err) {
                console.log('Could not load logo:', err.message);
            }
        }

        // Title (centered, below logo area)
        doc.y = 80; // Position below logo
        doc.fontSize(20).font('Helvetica-Bold').text('Change Management Report', { align: 'center' });
        doc.moveDown();
        doc.fontSize(12).font('Helvetica').text(`Generated: ${new Date().toLocaleDateString('en-GB')}`, { align: 'center' });
        doc.moveDown();

        // Filters info - display applied filters or "All"
        const hasFilters = (filters && (
            (filters.categories && filters.categories.length > 0) ||
            (filters.types && filters.types.length > 0) ||
            filters.dateFrom ||
            filters.dateTo
        ));

        if (hasFilters || filters) {
            doc.fontSize(10).font('Helvetica-Bold').text('Applied Filters:', { underline: true });

            // Category filter
            if (filters.categories && filters.allCategories) {
                const categoryText = (filters.categories.length === 0 || filters.categories.length === filters.allCategories.length)
                    ? 'All'
                    : filters.categories.join(', ');
                doc.font('Helvetica').text(`Category: ${categoryText}`);
            }

            // Type filter
            if (filters.types && filters.allTypes) {
                const typeText = (filters.types.length === 0 || filters.types.length === filters.allTypes.length)
                    ? 'All'
                    : filters.types.join(', ');
                doc.font('Helvetica').text(`Type of Change: ${typeText}`);
            }

            // Date filters
            if (filters.dateFrom) {
                doc.font('Helvetica').text(`Date From: ${filters.dateFrom}`);
            }
            if (filters.dateTo) {
                doc.font('Helvetica').text(`Date To: ${filters.dateTo}`);
            }

            doc.moveDown();
        }

        // Change Summary title
        doc.fontSize(18).font('Helvetica-Bold').text('Change Summary', 50, doc.y);
        doc.moveDown(2);

        // Sort data by start date (earliest to latest)
        const sortedData = [...data].sort((a, b) => {
            const dateA = a.start_date_obj ? new Date(a.start_date_obj) : new Date(0);
            const dateB = b.start_date_obj ? new Date(b.start_date_obj) : new Date(0);
            return dateA - dateB;
        });

        // Group sorted data by category
        const groupedByCategory = {};
        sortedData.forEach(item => {
            const category = item.category || 'Uncategorized';
            if (!groupedByCategory[category]) {
                groupedByCategory[category] = [];
            }
            groupedByCategory[category].push(item);
        });

        const marginLeft = 50;
        const contentWidth = 515;

        // Define different colors for each category
        const categoryColors = [
            '#00C853', // Green
            '#2196F3', // Blue
            '#FF9800', // Orange
            '#9C27B0', // Purple
            '#F44336', // Red
            '#00BCD4', // Cyan
            '#FF5722', // Deep Orange
            '#4CAF50'  // Light Green
        ];

        // Render each category group
        Object.keys(groupedByCategory).sort().forEach((category, catIndex) => {
            const changes = groupedByCategory[category];

            // Check if we need a new page for category header
            if (doc.y > 700) {
                doc.addPage();
            }

            // Category header with colored indicator and change count
            const categoryY = doc.y;
            const categoryColor = categoryColors[catIndex % categoryColors.length];

            // Colored circle indicator
            doc.circle(marginLeft + 5, categoryY + 8, 5)
               .fillAndStroke(categoryColor, categoryColor);

            // Category name and change count on same line
            doc.fontSize(14).font('Helvetica-Bold').fillColor('#000000');
            const categoryText = `${category}`;
            doc.text(categoryText, marginLeft + 20, categoryY + 2, { continued: false });

            // Calculate width of category text to position count right after it
            const categoryWidth = doc.widthOfString(categoryText, { fontSize: 14, font: 'Helvetica-Bold' });

            // Change count right after category name with spacing
            doc.fontSize(11).font('Helvetica').fillColor('#666666');
            doc.text(`  ${changes.length} changes`, marginLeft + 20 + categoryWidth, categoryY + 4);

            // Colored underline
            doc.moveTo(marginLeft, categoryY + 22)
               .lineTo(contentWidth + 50, categoryY + 22)
               .strokeColor(categoryColor)
               .lineWidth(3)
               .stroke();

            doc.y = categoryY + 30;

            // Render each change in this category
            changes.forEach((item, index) => {
                // Check if we need a new page
                const estimatedCardHeight = 150;
                if (doc.y + estimatedCardHeight > 720) {
                    doc.addPage();
                }

                const cardY = doc.y;
                const cardPadding = 15;

                // Card background
                doc.rect(marginLeft, cardY, contentWidth, 1) // Placeholder height, will adjust
                   .fillAndStroke('#ffffff', '#e0e0e0');

                // Change title/subject (bold, larger font)
                doc.fontSize(12).font('Helvetica-Bold').fillColor('#000000');
                const subjectText = item.subject || 'No Subject';
                doc.text(subjectText, marginLeft + cardPadding, cardY + cardPadding, {
                    width: contentWidth - 2 * cardPadding,
                    align: 'left'
                });

                doc.moveDown(0.5);

                // Metadata row: Type, Start, Impact (only 3 fields)
                const metaY = doc.y;
                doc.fontSize(9).font('Helvetica').fillColor('#666666');

                // Type
                doc.text('Type: ', marginLeft + cardPadding, metaY, { continued: true });
                doc.font('Helvetica-Bold').fillColor('#000000').text(item.type_of_change || 'N/A');

                // Start (date only, no time)
                const startDate = item.start_date_formatted || 'N/A';
                doc.font('Helvetica').fillColor('#666666');
                doc.text('Start: ', marginLeft + 200, metaY, { continued: true });
                doc.font('Helvetica-Bold').fillColor('#000000').text(startDate);

                // Impact
                doc.font('Helvetica').fillColor('#666666');
                doc.text('Impact: ', marginLeft + 340, metaY, { continued: true });
                doc.font('Helvetica-Bold').fillColor('#000000').text(item.impact_description || 'N/A');

                doc.moveDown(0.8);

                // Summary section
                if (item.explanation) {
                    const summaryY = doc.y;

                    // Summary header
                    doc.fontSize(10).font('Helvetica-Bold').fillColor('#000000');
                    doc.text('Summary', marginLeft + cardPadding, summaryY);

                    doc.moveDown(0.3);

                    // Summary text in italics - increased font from 9 to 10
                    doc.fontSize(10).font('Helvetica-Oblique').fillColor('#333333');
                    doc.text(item.explanation, marginLeft + cardPadding, doc.y, {
                        width: contentWidth - 2 * cardPadding,
                        align: 'left',
                        lineGap: 1
                    });
                }

                doc.moveDown(0.5);

                // Calculate actual card height
                const cardHeight = doc.y - cardY + cardPadding;

                // Draw card border
                doc.rect(marginLeft, cardY, contentWidth, cardHeight)
                   .stroke('#e0e0e0');

                doc.y = cardY + cardHeight + 15; // Space between cards
            });

            doc.moveDown(1); // Space between categories
        });

        // Footer
        doc.fontSize(8).fillColor('#999999').text(
            `Change Management Report - Page ${doc.bufferedPageRange().count}`,
            50,
            750,
            { align: 'center' }
        );

        // Finalize PDF
        doc.end();

    } catch (error) {
        console.error('Error generating PDF:', error);
        if (!res.headersSent) {
            res.status(500).json({
                error: 'Error generating PDF',
                details: error.message
            });
        }
    }
});

// Start server
app.listen(PORT, () => {
    console.log(`Change Enablement App running at http://localhost:${PORT}`);
    console.log(`Open your browser and navigate to http://localhost:${PORT}`);
    if (!process.env.ANTHROPIC_API_KEY) {
        console.warn('WARNING: ANTHROPIC_API_KEY not found in .env file. AI explanations will use fallback mode.');
    }
});
