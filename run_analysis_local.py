
from backend.storage import SQLAlchemyStorage, db
from ai_module.pipeline import run_pipeline
from backend.app import app

def regenerate_insights():
    with app.app_context():
        print("Initializing Storage...")
        storage = SQLAlchemyStorage(db)
        
        # We can optionally clear old processed flags to force re-analysis 
        # but run_pipeline usually picks up unprocessed.
        # If user wants to RE-generate on existing data, we might need to reset 'processed=False' for some feedback.
        # For now, let's assume there is feedback or we just run on what's there.
        # Actually, let's inject a few sample feedbacks if none exist to ensure we see results.
        


        print("Checking for feedback...")
        from backend.storage import Feedback
        
        total = Feedback.query.count()
        print(f"Total Feedback in DB: {total}")

        # Reset processed status for DEMO purposes to allow regeneration
        print("Resetting 'processed' flags to force regeneration...")
        count = Feedback.query.update({Feedback.processed: False})
        db.session.commit()
        print(f"Marked {count} items as unprocessed.")


        print("Running Pipeline with Gemini...")
        result = run_pipeline(storage, institute_id=None) # Process all or default
        
        print("Pipeline Result:", result)
        print("Done. Insights regenerated.")

if __name__ == "__main__":
    regenerate_insights()
