import time
import subprocess
import datetime
import sys

# Configuration
INTERVAL_HOURS = 3
SCRIPT_TO_RUN = "quick_start.py"

def run_pipeline():
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n[{timestamp}] [SCHEDULER] Waking up. Starting {SCRIPT_TO_RUN}...")
    
    # We use subprocess so that if quick_start.py calls sys.exit(), 
    # it doesn't kill this scheduler script.
    try:
        # '-u' forces unbuffered output so logs show up immediately in Docker
        result = subprocess.run(
            [sys.executable, "-u", SCRIPT_TO_RUN], 
            text=True, 
            capture_output=False
        )
        
        if result.returncode == 0:
            print(f"[{timestamp}] [SCHEDULER] Pipeline finished successfully.")
        else:
            print(f"[{timestamp}] [SCHEDULER] Pipeline failed with exit code {result.returncode}.")
            
    except Exception as e:
        print(f"[{timestamp}] [SCHEDULER] Error running subprocess: {e}")

def main():
    print("=======================================")
    print("   THOR SEIZURE SCHEDULER STARTED")
    print(f"   Running every {INTERVAL_HOURS} hours")
    print("=======================================")
    
    # Run once immediately on startup
    run_pipeline()
    
    while True:
        # Calculate next run time for log clarity
        next_run = datetime.datetime.now() + datetime.timedelta(hours=INTERVAL_HOURS)
        print(f"\n[SCHEDULER] Sleeping... Next run at approx {next_run.strftime('%H:%M')}")
        
        # Sleep for 3 hours (10800 seconds)
        time.sleep(INTERVAL_HOURS * 3600)
        
        run_pipeline()

if __name__ == "__main__":
    # Ensure our own scheduler logs are printed immediately
    sys.stdout.reconfigure(line_buffering=True)
    main()
