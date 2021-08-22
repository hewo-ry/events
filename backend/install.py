from core.database import SessionLocal

db = SessionLocal()

try:
    print("Installation done.")

    # TODO add installation stuff

    db.commit()

except (KeyboardInterrupt, ValueError) as e:
    print(e)
    print("Installation halted.")

finally:
    db.close()
