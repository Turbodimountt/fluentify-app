
import sys
import os
import asyncio
from sqlalchemy import select, func, delete

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.database import AsyncSessionLocal
from app.models.models import ProfessionalContext

async def check_duplicates():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(ProfessionalContext))
        contexts = result.scalars().all()
        print(f"Total contexts found: {len(contexts)}")
        for ctx in contexts:
            print(f"- {ctx.name} ({ctx.slug}) id: {ctx.id}")
        
        # Identify duplicates by slug
        seen = {}
        to_delete = []
        for ctx in contexts:
            if ctx.slug in seen:
                to_delete.append(ctx.id)
            else:
                seen[ctx.slug] = ctx.id
        
        if to_delete:
            print(f"Deleting {len(to_delete)} duplicate(s)...")
            await db.execute(delete(ProfessionalContext).where(ProfessionalContext.id.in_(to_delete)))
            await db.commit()
            print("Done.")
        else:
            print("No duplicates found.")

if __name__ == "__main__":
    asyncio.run(check_duplicates())
