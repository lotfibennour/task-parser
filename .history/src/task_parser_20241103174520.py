from dateparser import parse
from datetime import datetime
import re
from typing import Optional, Dict
import pytz

class TaskParser:
  def __init__(self, timezone: str = 'Europe/Paris'):
      self.timezone = pytz.timezone(timezone)
      
  def extract_url(self, text: str) -> Optional[str]:
      url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\$\$,]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
      urls = re.findall(url_pattern, text)
      return urls[0] if urls else None

  def extract_time_range(self, text: str) -> tuple[Optional[datetime], Optional[datetime]]:
      # Common French time patterns
      time_range_patterns = [
          r'de (\d{1,2})[h:](\d{2})? à (\d{1,2})[h:](\d{2})?',
          r'de (\d{1,2}) à (\d{1,2})',
          r'(\d{1,2})[h:](\d{2})? - (\d{1,2})[h:](\d{2})?'
      ]
      
      for pattern in time_range_patterns:
          match = re.search(pattern, text.lower())
          if match:
              groups = match.groups()
              if len(groups) == 2:  # Simple hour format
                  start_time = f"{groups[0]}:00"
                  end_time = f"{groups[1]}:00"
              else:  # Hour:minute format
                  start_time = f"{groups[0]}:{groups[1] or '00'}"
                  end_time = f"{groups[2]}:{groups[3] or '00'}"
              
              # Parse the date part
              date_part = re.sub(pattern, '', text)
              base_date = parse(date_part, languages=['fr'])
              
              if base_date:
                  # Combine date and times
                  start_hour, start_minute = map(int, start_time.split(':'))
                  end_hour, end_minute = map(int, end_time.split(':'))
                  
                  start_datetime = base_date.replace(hour=start_hour, minute=start_minute)
                  end_datetime = base_date.replace(hour=end_hour, minute=end_minute)
                  
                  return start_datetime, end_datetime
      
      # If no time range is found, try to parse a single datetime
      single_datetime = parse(text, languages=['fr'])
      if single_datetime:
          return single_datetime, None
          
      return None, None

  def parse_task(self, text: str) -> Dict:
      # Remove URL from text for better date parsing
      url = self.extract_url(text)
      text_without_url = re.sub(r'http[s]?://\S+', '', text).strip()
      
      # Extract time information
      start_time, end_time = self.extract_time_range(text_without_url)
      
      # Extract task name (first sentence or until the first time indicator)
      name_patterns = [
          r'^([^.!?\n]+)',  # First sentence
          r'^(.*?)(?:demain|aujourd\'hui|le \d{1,2}|lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)',  # Until first time indicator
      ]
      
      task_name = text_without_url
      for pattern in name_patterns:
          match = re.search(pattern, text_without_url, re.IGNORECASE)
          if match:
              task_name = match.group(1).strip()
              break
      
      # Extract description (everything after task name)
      description = text_without_url[len(task_name):].strip()
      if not description:
          description = task_name
          
      return {
          "name": task_name,
          "description": description,
          "due_date": start_time.isoformat() if start_time else None,
          "completion_date": end_time.isoformat() if end_time else None,
          "status": "pending",
          "url": url
      }