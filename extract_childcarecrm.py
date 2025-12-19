"""
Code Ninjas Tour Slot Extractor - ChildcareCRM Calendar
=======================================================

HTML Structure (from your screenshots):
<a class="fc-day-grid-event fc-h-event fc-event fc-start fc-end available-tour-time">
  <div class="fc-content">
    <span class="fc-time">10:00 AM</span>
    <span class="fc-title">&nbsp;</span>
  </div>
</a>

Parent: <td class="fc-event-container" data-date="2026-01-06">

Navigation: button.fc-next-button in .fc-toolbar.fc-header-toolbar

Version: 1.2 - Optimized for ChildcareCRM
"""

from playwright.async_api import async_playwright
import asyncio
import json
from datetime import datetime
import re


class CodeNinjasCalendarExtractor:
    """Extract tour slots from ChildcareCRM/FullCalendar"""
    
    def __init__(self, calendar_url, location_id="WDM"):
        self.calendar_url = calendar_url
        self.location_id = location_id
        self.run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def convert_time_to_24h(self, time_str):
        """Convert '10:00 AM' to '10:00' (24h format)"""
        if not time_str:
            return None
        
        time_str = str(time_str).strip()
        
        # Already 24h format
        if re.match(r'^\d{2}:\d{2}$', time_str):
            return time_str
        
        # Parse 12h format (10:00 AM, 4:00 PM, etc.)
        match = re.search(r'(\d{1,2}):(\d{2})\s*(AM|PM)', time_str, re.IGNORECASE)
        if match:
            hour, minute, period = match.groups()
            hour = int(hour)
            period = period.upper()
            
            if period == 'PM' and hour != 12:
                hour += 12
            elif period == 'AM' and hour == 12:
                hour = 0
            
            return f"{hour:02d}:{minute}"
        
        return None
    
    async def extract_slots_from_page(self, page, week_index):
        """Extract all available tour time slots from current calendar view"""
        
        print(f"Extracting slots for week {week_index}...")
        
        # Count available slots
        slot_count = await page.locator('a.available-tour-time').count()
        
        if slot_count == 0:
            print(f"⚠️ No available slots for week {week_index}")
            return []
        
        print(f"✓ Found {slot_count} available slots")
        
        # Extract slot data using JavaScript
        slots = await page.evaluate('''() => {
            // Find all available tour time slots
            const slotElements = document.querySelectorAll('a.available-tour-time');
            const results = [];
            
            slotElements.forEach((el, index) => {
                try {
                    // Get time from fc-time span
                    const timeSpan = el.querySelector('.fc-time');
                    const time = timeSpan ? timeSpan.textContent.trim() : el.textContent.trim();
                    
                    // Get date from parent td element
                    let date = null;
                    const parentTd = el.closest('td.fc-event-container');
                    if (parentTd) {
                        date = parentTd.getAttribute('data-date');
                    }
                    
                    // If still no date, check other parent elements
                    if (!date) {
                        const dayCell = el.closest('td[data-date]');
                        if (dayCell) {
                            date = dayCell.getAttribute('data-date');
                        }
                    }
                    
                    // Get element classes for creating selector
                    const classes = el.className.split(' ').filter(c => c).join('.');
                    
                    results.push({
                        date: date,
                        time: time,
                        selector: `a.${classes}`,
                        index: index
                    });
                } catch (e) {
                    console.error('Error extracting slot:', e);
                }
            });
            
            return results;
        }''')
        
        # Process and validate slots
        processed_slots = []
        for slot in slots:
            if slot['date'] and slot['time']:
                time_24h = self.convert_time_to_24h(slot['time'])
                
                processed_slots.append({
                    'iso_date': slot['date'],  # Already in YYYY-MM-DD format
                    'display_date': slot['date'],
                    'time_12h': slot['time'],
                    'time_24h': time_24h or slot['time'],
                    'element_selector': f"a.available-tour-time:nth-of-type({slot['index'] + 1})",
                    'week_index': week_index
                })
        
        print(f"✓ Processed {len(processed_slots)} valid slots")
        return processed_slots
    
    async def click_next_week(self, page):
        """Click the next button in FullCalendar toolbar"""
        
        print("Navigating to next week...")
        
        try:
            # FullCalendar next button
            await page.click('button.fc-next-button', timeout=5000)
            print("✓ Clicked next week button")
            return True
            
        except Exception as e:
            print(f"⚠️ Could not click next button: {e}")
            
            # Fallback: keyboard navigation
            try:
                await page.keyboard.press('ArrowRight')
                print("✓ Used keyboard navigation")
                return True
            except:
                return False
    
    async def wait_for_calendar_update(self, page):
        """Wait for calendar to update after navigation"""
        
        try:
            # Wait for network to be idle
            await page.wait_for_load_state('networkidle', timeout=5000)
        except:
            pass  # Continue even if timeout
        
        # Additional wait for DOM updates
        await page.wait_for_timeout(2000)
        
        print("✓ Calendar updated")
    
    async def extract_all_weeks(self):
        """Extract slots from all 4 weeks"""
        
        print(f"\n{'='*70}")
        print(f"Code Ninjas Calendar Extraction - ChildcareCRM")
        print(f"Location: {self.location_id}")
        print(f"URL: {self.calendar_url}")
        print(f"Run ID: {self.run_id}")
        print(f"{'='*70}\n")
        
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(
                headless=True,  # Set to False to watch it run
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 900}
            )
            
            page = await context.new_page()
            
            try:
                # Navigate to calendar
                print(f"Loading calendar...")
                await page.goto(self.calendar_url, wait_until='networkidle', timeout=30000)
                
                # Wait for calendar to load
                await page.wait_for_selector('.fc-view-container', timeout=10000)
                await page.wait_for_timeout(3000)  # Extra wait for rendering
                
                print("✓ Calendar loaded\n")
                
                all_weeks = []
                
                # Extract each week
                for week_index in range(4):
                    print(f"--- Week {week_index} ---")
                    
                    # Extract slots from current view
                    slots = await self.extract_slots_from_page(page, week_index)
                    
                    week_label = ['Current Week', 'Next Week', 'Week 3', 'Week 4'][week_index]
                    
                    all_weeks.append({
                        'week_number': week_index,
                        'week_label': week_label,
                        'slot_count': len(slots),
                        'slots': slots
                    })
                    
                    # Navigate to next week (if not the last)
                    if week_index < 3:
                        success = await self.click_next_week(page)
                        
                        if not success:
                            print(f"⚠️ Navigation failed for week {week_index + 1}")
                        
                        await self.wait_for_calendar_update(page)
                    
                    print()  # Blank line between weeks
                
                await browser.close()
                
                # Build final result
                total_slots = sum(w['slot_count'] for w in all_weeks)
                
                result = {
                    'extraction_metadata': {
                        'run_id': self.run_id,
                        'location_id': self.location_id,
                        'timestamp': datetime.now().isoformat(),
                        'calendar_url': self.calendar_url,
                        'calendar_type': 'childcarecrm_fullcalendar',
                        'total_weeks_extracted': len(all_weeks),
                        'total_unique_slots': total_slots
                    },
                    'weeks': all_weeks,
                    'summary': {
                        'slots_by_week': {
                            w['week_label']: w['slot_count'] 
                            for w in all_weeks
                        },
                        'total_slots': total_slots
                    }
                }
                
                print(f"{'='*70}")
                print(f"✅ EXTRACTION COMPLETE")
                print(f"{'='*70}")
                print(f"Total slots extracted: {total_slots}")
                print(f"\nBreakdown:")
                for week in all_weeks:
                    print(f"  {week['week_label']}: {week['slot_count']} slots")
                print(f"{'='*70}\n")
                
                return result
                
            except Exception as e:
                await browser.close()
                print(f"\n❌ ERROR: {e}\n")
                import traceback
                traceback.print_exc()
                raise e


async def main():
    """Main entry point"""
    import sys
    
    # Get command line arguments
    if len(sys.argv) < 2:
        print("Usage: python extract_childcarecrm.py <calendar_url> [location_id]")
        print("\nExample:")
        print("  python extract_childcarecrm.py 'https://your-calendar.com' 'WDM'")
        sys.exit(1)
    
    calendar_url = sys.argv[1]
    location_id = sys.argv[2] if len(sys.argv) > 2 else "WDM"
    
    # Run extraction
    extractor = CodeNinjasCalendarExtractor(calendar_url, location_id)
    result = await extractor.extract_all_weeks()
    
    # Output JSON
    print(json.dumps(result, indent=2))
    
    return result


if __name__ == "__main__":
    asyncio.run(main())
