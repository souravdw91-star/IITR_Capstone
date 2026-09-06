"""
Dataset Loader & Evaluation Runner script.
Processes development_tickets.json and validation_tickets.json through the pipeline
and populates storage/decisions.db with full audit decision records.
"""
import os
import json
import time

from src.pipeline import SupportPipeline


def load_datasets_into_db():
    print("=== Loading Capstone Ticket Datasets into SQLite Database ===")

    dev_tickets_path = "FDE_Capstone_Docs/05_Datasets/development_tickets.json"
    val_tickets_path = "FDE_Capstone_Docs/05_Datasets/validation_tickets.json"

    if not os.path.exists(dev_tickets_path) or not os.path.exists(val_tickets_path):
        print(f"Error: Dataset files not found at '{dev_tickets_path}' or '{val_tickets_path}'")
        return

    with open(dev_tickets_path, "r", encoding="utf-8") as f:
        dev_tickets = json.load(f)

    with open(val_tickets_path, "r", encoding="utf-8") as f:
        val_tickets = json.load(f)

    all_tickets = dev_tickets + val_tickets
    print(f"Total tickets to process and load into DB: {len(all_tickets)} (500 dev + 80 val)")

    pipeline = SupportPipeline(db_path="storage/decisions.db")

    auto_count = 0
    esc_count = 0
    blocked_count = 0
    start_time = time.time()

    for idx, raw_ticket in enumerate(all_tickets, 1):
        res = pipeline.process_ticket(raw_ticket)

        if res.action_taken == "auto_respond":
            auto_count += 1
        elif res.action_taken == "escalate":
            esc_count += 1
        elif res.action_taken == "blocked":
            blocked_count += 1

        if idx % 100 == 0 or idx == len(all_tickets):
            print(f"  Processed {idx}/{len(all_tickets)} tickets...")

    total_time = time.time() - start_time
    total_db_count = pipeline.logger.get_decision_count()

    print("\n=== Dataset Loading Complete ===")
    print(f"Total Database Decision Records: {total_db_count}")
    print(f"Auto-Responses Logged:           {auto_count}")
    print(f"Escalations Logged:              {esc_count}")
    print(f"Guardrail Blocks Logged:         {blocked_count}")
    print(f"Total Execution Time:            {total_time:.2f} seconds\n")


if __name__ == "__main__":
    load_datasets_into_db()
