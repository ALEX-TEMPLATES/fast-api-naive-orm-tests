.PHONY: help mm uh

# Capture all arguments except the target name itself
ARGS = $(filter-out $@,$(MAKECMDGOALS))

help:
	@echo "Available targets:"
	@echo "  mm <migration_message> - Creates a new Alembic revision with autogenerate."
	@echo "                             Example: make mm add_new_field"
	@echo "                             For messages with spaces, use quotes: make mm \"add new field\""
	@echo "  uh                     - Upgrades the database to the latest revision (alembic upgrade head)."

# Database migrations
mm:
ifeq ($(strip $(ARGS)),)
	$(error Migration message is not provided. Usage: make mm <your_message>)
endif
	@echo "Creating new Alembic revision (autogenerate) with message: $(ARGS)"
	(cd src && alembic revision -m "$(ARGS)" --autogenerate)

uh:
	@echo "Upgrading database to head..."
	(cd src && alembic upgrade head)
