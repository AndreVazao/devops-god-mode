# Guided Mobile Command Center

## Routes

- `/api/guided-command-center/status`
- `/api/guided-command-center/package`
- `/api/guided-command-center/dashboard`
- `/api/guided-command-center/actions`
- `/api/guided-command-center/projects/{project}/brief`
- `/api/guided-command-center/prompt`
- `/api/guided-command-center/execute`
- `/app/guided-command-center`

## Objective

Make God Mode brutally easier to use on mobile. The operator does not need to remember command wording. The cockpit offers guided buttons that generate strong prompts using AndreOS Memory Core and submit them through Mission Control.

## Guided actions

- Continue project
- Deep audit
- Build check
- Fix plan
- Memory review
- Delivery summary

## Flow

1. Select project.
2. Select guided action.
3. Optionally add extra instruction.
4. The service builds a full command from the template.
5. It reads AndreOS project memory and attaches project brief.
6. It submits the command to Mission Control.
7. Mission Control creates the approval card.
8. The action is logged in project history.

## Safety

Guided Command Center does not bypass approvals. Write/destructive flows remain behind Mission Control and Mobile Approval Cockpit.
