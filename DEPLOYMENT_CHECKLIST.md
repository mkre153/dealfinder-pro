# DealFinder Pro - Deployment Checklist

Use this checklist to ensure proper deployment of DealFinder Pro.

---

## Pre-Deployment

### 1. System Requirements

- [ ] Python 3.9+ installed
- [ ] PostgreSQL 13+ installed and running (or MySQL 8+)
- [ ] Chrome or Firefox browser installed (for scraping)
- [ ] Sufficient disk space (minimum 10GB recommended)
- [ ] Network access to GoHighLevel API (if using GHL)

### 2. Installation

- [ ] Repository cloned or files copied to deployment location
- [ ] Virtual environment created: `python3 -m venv venv`
- [ ] Virtual environment activated
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] All required directories created (logs, reports, backups, data)

### 3. Configuration Files

- [ ] `.env` file created from `.env.example`
- [ ] Database credentials added to `.env`
- [ ] Email credentials added to `.env` (if using email notifications)
- [ ] GHL API credentials added to `.env` (if using GHL integration)
- [ ] `config.json` reviewed and customized
- [ ] Target locations configured in `config.json`
- [ ] Search criteria configured (price range, bedrooms, etc.)
- [ ] Scoring weights adjusted to preferences

### 4. Database Setup

- [ ] PostgreSQL database created: `createdb dealfinder`
- [ ] Schema initialized: `psql dealfinder < database/schema.sql`
- [ ] Database connection tested: `python main.py --test-db`
- [ ] Sample data loaded (optional): `psql dealfinder < database/sample_data.sql`
- [ ] Backup strategy configured

### 5. GoHighLevel Setup (if enabled)

- [ ] GHL API key generated
- [ ] Location ID obtained
- [ ] Custom fields created in GHL (see GHL_SETUP_GUIDE.md)
  - [ ] Contact custom fields for buyers
  - [ ] Opportunity custom fields for properties
- [ ] Pipeline created and configured
- [ ] Pipeline stages created
- [ ] Workflow(s) created
  - [ ] Hot Deal Alert workflow
  - [ ] Buyer Match Notification workflow
  - [ ] Follow-up Sequence workflow (optional)
- [ ] Workflow IDs added to `config.json`
- [ ] Pipeline IDs added to `config.json`
- [ ] GHL connection tested: `python main.py --test-ghl`

### 6. Email Setup

- [ ] SMTP server configured (Gmail, SendGrid, etc.)
- [ ] App password generated (if using Gmail)
- [ ] Email templates reviewed in `templates/`
- [ ] Sender email verified
- [ ] Recipient email configured
- [ ] Test email sent (run workflow in test mode)

---

## Testing

### 7. Component Testing

- [ ] Database connection: `python main.py --test-db`
- [ ] GHL connection: `python main.py --test-ghl`
- [ ] Test scrape: `python main.py --test-scrape 90210`
- [ ] Unit tests: `pytest tests/test_integration.py -v`
- [ ] Verify logs are being created in `logs/`

### 8. Workflow Testing

- [ ] Set `DRY_RUN=true` in `.env`
- [ ] Run full workflow: `python main.py --full-workflow`
- [ ] Review logs for errors
- [ ] Verify properties scraped
- [ ] Verify properties analyzed
- [ ] Verify scores calculated correctly
- [ ] Verify reports generated in `reports/`
- [ ] Review HTML email report
- [ ] Review Excel report
- [ ] Verify no GHL opportunities created (dry run mode)

### 9. GHL Integration Testing

- [ ] Set `DRY_RUN=false` in `.env`
- [ ] Import test buyers into GHL
- [ ] Run workflow with small dataset (1-2 ZIP codes)
- [ ] Verify opportunities created in GHL
- [ ] Verify custom fields populated correctly
- [ ] Verify workflows triggered
- [ ] Verify tasks created
- [ ] Verify buyer matching works
- [ ] Verify SMS notifications (if enabled)

---

## Production Deployment

### 10. Security

- [ ] `.env` file permissions restricted: `chmod 600 .env`
- [ ] `.gitignore` includes `.env`
- [ ] Database password is strong
- [ ] API keys are valid and restricted to necessary permissions
- [ ] SMTP credentials secured
- [ ] Webhook URLs use HTTPS (if applicable)
- [ ] Firewall rules configured (if needed)

### 11. Scheduling

Choose one scheduling method:

#### Option A: Cron (Linux/Mac)

- [ ] Edit crontab: `crontab -e`
- [ ] Add daily schedule:
  ```
  0 8 * * * cd /path/to/Real\ Estate\ Valuation && /path/to/venv/bin/python main.py --full-workflow >> logs/cron.log 2>&1
  ```
- [ ] Verify cron job: `crontab -l`
- [ ] Test cron execution

#### Option B: Task Scheduler (Windows)

- [ ] Open Task Scheduler
- [ ] Create Basic Task
- [ ] Set trigger: Daily at desired time
- [ ] Set action: Start Program
  - Program: `C:\path\to\venv\Scripts\python.exe`
  - Arguments: `main.py --full-workflow`
  - Start in: `C:\path\to\Real Estate Valuation`
- [ ] Test task execution

#### Option C: Supervisor (Production)

- [ ] Install supervisor: `sudo apt-get install supervisor`
- [ ] Create supervisor config
- [ ] Start supervisor
- [ ] Verify process running

### 12. Monitoring

- [ ] Log rotation configured
- [ ] Disk space monitoring enabled
- [ ] Error alerts configured (email on failure)
- [ ] Database backup scheduled (daily recommended)
- [ ] Performance metrics baseline established
- [ ] Uptime monitoring (if using web service)

### 13. Backup Strategy

- [ ] Database backup script created
- [ ] Backup location configured
- [ ] Backup schedule configured (daily minimum)
- [ ] Backup retention policy defined
- [ ] Restore procedure documented and tested
- [ ] Config files backed up
- [ ] `.env` file backed up securely (encrypted)

---

## Post-Deployment

### 14. Initial Run

- [ ] First production run executed
- [ ] Results reviewed
- [ ] Logs checked for errors
- [ ] Email report received
- [ ] Excel report generated
- [ ] GHL opportunities created
- [ ] Hot deals identified
- [ ] Buyers notified

### 15. Optimization

- [ ] Review scoring accuracy
- [ ] Adjust scoring weights if needed
- [ ] Fine-tune search criteria
- [ ] Optimize database queries (if slow)
- [ ] Adjust rate limiting (if needed)
- [ ] Configure connection pool size
- [ ] Enable/disable optional features

### 16. Documentation

- [ ] Document any custom configurations
- [ ] Document scheduled job details
- [ ] Document backup/restore procedures
- [ ] Create runbook for common operations
- [ ] Document troubleshooting steps
- [ ] Train team members on system use

---

## Maintenance

### 17. Regular Tasks

**Daily:**
- [ ] Review workflow logs
- [ ] Check for errors
- [ ] Verify email reports received

**Weekly:**
- [ ] Review opportunity scores
- [ ] Check GHL sync status
- [ ] Review buyer matches
- [ ] Clean up old logs (optional)

**Monthly:**
- [ ] Review and update buyer profiles in GHL
- [ ] Analyze market trends from reports
- [ ] Update search criteria if needed
- [ ] Review scoring weights
- [ ] Test database backup restore
- [ ] Update dependencies: `pip install -r requirements.txt --upgrade`

**Quarterly:**
- [ ] Rotate API keys
- [ ] Review and optimize database
- [ ] Archive old data
- [ ] System performance review
- [ ] Update Python dependencies

### 18. Troubleshooting

**If workflow fails:**
1. Check logs in `logs/app_YYYYMMDD.log`
2. Verify all services running (database, etc.)
3. Test individual components
4. Check network connectivity
5. Review error email (if received)

**If no properties found:**
1. Verify target locations are valid
2. Check date range (`days_back`)
3. Test scraping manually
4. Review search criteria
5. Check for website changes

**If GHL sync fails:**
1. Test GHL connection: `python main.py --test-ghl`
2. Verify API key is valid
3. Check custom field names match
4. Review GHL API logs
5. Verify pipeline/workflow IDs

---

## Performance Benchmarks

Record your baseline performance:

- **Workflow Duration**: _______ seconds
- **Properties Scraped per Location**: _______
- **Properties Analyzed per Minute**: _______
- **Database Query Time**: _______ ms
- **Report Generation Time**: _______ seconds
- **GHL Sync Time**: _______ seconds

---

## Support Contacts

- **Database Admin**: _______________________
- **GHL Admin**: _______________________
- **Email/SMTP Support**: _______________________
- **System Administrator**: _______________________

---

## Version History

| Version | Date | Changes | Deployed By |
|---------|------|---------|-------------|
| 1.0.0 | YYYY-MM-DD | Initial deployment | _________ |
|  |  |  | |
|  |  |  | |

---

## Sign-Off

- [ ] All checklist items completed
- [ ] System tested and verified
- [ ] Documentation reviewed
- [ ] Team trained
- [ ] Ready for production

**Deployed By**: _________________ **Date**: _________

**Reviewed By**: _________________ **Date**: _________

---

**Congratulations! DealFinder Pro is now deployed and ready to find investment opportunities!** 🎉
