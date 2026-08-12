# Dual Approval System - Testing Guide

## Prerequisites

- Application running locally or deployed
- Access to demo credentials (technical.analista.tecnologia / Demo1234!)
- At least one idea in the technical queue with:
  - Basic validation complete
  - Architecture package generated
  - Economics analysis available

## Test Scenarios

### Scenario 1: Complete Approval Workflow

**Objective:** Validate the entire dual approval process from chat to PDF download

**Steps:**

1. **Login as Technical Reviewer**
   ```
   URL: http://localhost:5173 (or deployed URL)
   Username: analista.tecnologia
   Password: Demo1234!
   ```
   - Expected: Login successful, redirected to technical queue

2. **View Technical Queue**
   - Expected: See list of ideas with approval status panel
   - Check: Each idea shows:
     - "○ Pendiente" for agent approval
     - "○ Pendiente" for human approval

3. **Open Technical Chat**
   - Find idea with title (e.g., "Sistema Predictor...")
   - Click "Chat técnico con agente" button
   - Expected: Chat interface appears with input field

4. **Send Message to Agent**
   - Type: "¿Cuál es la complejidad de integración con la arquitectura actual?"
   - Press Enter or click "Enviar"
   - Expected:
     - Message appears in blue bubble (right side)
     - Agent response appears in gray bubble (left side)
     - Response includes structured questions
     - Chat history grows

5. **Continue Chat Conversation**
   - Ask follow-up: "¿Qué componentes requieren refactoring?"
   - Expected: Agent provides specific component recommendations
   - Chat history expands with multiple exchanges

6. **Agent Approval**
   - Click "Aprobar (Agente IA)" button
   - Dialog appears with text area for approval summary
   - Type summary: "Idea técnicamente viable. Integración con componentes existentes es straightforward. Requiere validación de seguridad adicional en fase de desarrollo."
   - Click "Confirmar aprobación"
   - Expected:
     - Dialog closes
     - Approval status updates to "✓ Aprobado" for agent
     - Chat button disappears
     - Agent approval button disappears
     - "Aprobar" button becomes enabled (green/primary color)

7. **Human Approval**
   - Click "Aprobar" button
   - Expected:
     - Request succeeds
     - Human approval status updates to "✓ Aprobado"
     - Idea status shows both approvals complete
     - PDF download button becomes enabled

8. **Download Architecture PDF**
   - Click "Descargar arquitectura (PDF)" button
   - Expected:
     - PDF file downloads with name `architecture-package-{idea-id}.pdf`
     - File contains 9 sections:
       1. Executive Summary
       2. Architecture Diagram
       3. Components
       4. Integrations
       5. Risks
       6. Deployment Steps
       7. Cost Analysis
       8. ROI Metrics
       9. Contact Information

9. **Verify Queue Updates**
   - Refresh page or wait for polling (10 seconds)
   - Expected: Idea no longer appears in "Pending Technical Review" queue
   - Idea moves to appropriate next stage

**Success Criteria:**
- ✅ Chat interface functional and responsive
- ✅ Agent provides meaningful responses
- ✅ Agent approval summary accepted
- ✅ Human approval button only enables after agent approval
- ✅ PDF downloads successfully after both approvals
- ✅ All UI states reflect approval progress

---

### Scenario 2: Reject Without Approval

**Objective:** Verify that rejection workflow works at any stage without requiring approvals

**Steps:**

1. **View Technical Queue**
   - Login as technical reviewer

2. **Reject Before Agent Approval**
   - Select idea without any approvals
   - Click "Rechazar idea" button
   - Prompt appears: "Proporciona el motivo técnico del rechazo (mínimo 5 caracteres):"
   - Type: "Arquitectura no escalable para producción"
   - Expected:
     - Rejection accepted
     - Idea moves to rejected status
     - No longer appears in technical queue
     - Notification confirms "Idea rechazada"

3. **Test Rejection at Each Stage**
   - Repeat with idea after agent approval
   - Expected: Rejection works regardless of approval state

**Success Criteria:**
- ✅ Rejection available at all stages
- ✅ Minimum character validation enforced
- ✅ Rejection reason stored
- ✅ Idea removed from queue

---

### Scenario 3: Move to Funding with Gate Override

**Objective:** Verify economic gate and override functionality during dual approval

**Steps:**

1. **Check Idea Economics**
   - Look for economics panel on technical queue item
   - Check verdict (favorable, acceptable, marginal, unfavorable)

2. **Move to Funding (Favorable or Acceptable)**
   - If economics verdict is favorable (≥3.0x ratio):
     - Click "Pasar a funding"
     - Expected: Moves immediately without override prompt

3. **Move to Funding (Marginal, Need Override)**
   - If economics verdict is marginal (≥1.0x, <3.0x):
     - Click "Pasar a funding"
     - Expected: 
       - Confirmation dialog appears
       - Message shows economic verdict and ratio
       - Ask for override confirmation

4. **Confirm Override**
   - Click "Continuar de todas formas" or "Yes" in dialog
   - Expected: Idea moves to funding stage despite economic gate

**Success Criteria:**
- ✅ Economic gate enforces minimum ratio
- ✅ Override available for marginal ideas
- ✅ Favorable/acceptable bypass gate
- ✅ Message explains economics to user

---

### Scenario 4: Multi-Language Support

**Objective:** Verify translations display correctly in all languages

**Steps:**

1. **Switch Language to English**
   - Find language selector (top navigation)
   - Select "English"
   - Expected:
     - "Technical Chat" button visible
     - "Approve (AI Agent)" button visible
     - "Approve" button text updates
     - All error messages in English

2. **Verify Chat Interface English**
   - Click "Technical Chat"
   - Placeholder text: "Ask technical clarifications to the agent..."
   - Button: "Send"
   - Expected: All UI text in English

3. **Switch Language to Portuguese**
   - Select "Português"
   - Expected:
     - "Chat tecnico com agente" button
     - "Aprovar (Agente IA)" button
     - All text in Portuguese

4. **Verify Each Language**
   - Spanish (ES): Checked
   - English (EN): Checked
   - Portuguese (PT): Checked

**Success Criteria:**
- ✅ All labels translate correctly
- ✅ All buttons translate correctly
- ✅ Error messages translate correctly
- ✅ Placeholders translate correctly
- ✅ No missing translations

---

### Scenario 5: Error Conditions

**Objective:** Verify error handling and user guidance

**Steps:**

1. **Chat Without Input**
   - Click "Chat" button to open chat
   - Click "Send" without typing message
   - Expected: Nothing happens (button ignored or disabled)

2. **Approve Agent Without Chat**
   - Click "Approve (AI Agent)"
   - Dialog appears
   - Click "Confirmar aprobación" without text
   - Expected: Alert/error message: "Por favor escribe un resumen de aprobación"

3. **Approve Human Before Agent**
   - (Only possible via direct API attempt)
   - Expected API Response:
     ```json
     {
       "detail": "El agente IA debe aprobar la idea primero"
     }
     ```

4. **Download PDF Before Approval**
   - Try to manually call download endpoint without approvals
   - Expected: Button disabled with tooltip "Disponible después de aprobación humana"

**Success Criteria:**
- ✅ Empty chat message handled gracefully
- ✅ Empty approval summary prevented
- ✅ Approval sequence enforced
- ✅ PDF download properly disabled
- ✅ User messages are clear and helpful

---

### Scenario 6: API Endpoint Validation

**Objective:** Verify backend endpoints work correctly via API

**Steps:**

1. **Get Authentication Token**
   ```bash
   curl -X POST http://localhost:8000/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"analista.tecnologia","password":"Demo1234!"}'
   ```
   - Expected: Returns JWT token

2. **Get Technical Queue**
   ```bash
   curl -X GET http://localhost:8000/ideas/technical-queue \
     -H "Authorization: Bearer {token}"
   ```
   - Expected: Returns array of technical queue items with approval status

3. **Send Technical Chat Message**
   ```bash
   curl -X POST http://localhost:8000/ideas/{idea_id}/technical-chat \
     -H "Authorization: Bearer {token}" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "¿Cuál es la complejidad de integración?",
       "question_type": "technical_clarification"
     }'
   ```
   - Expected: 
     - Status: 200 OK
     - Response includes:
       - interaction_id
       - agent_response
       - agent_questions array
       - next_steps
       - created_at

4. **Submit Agent Approval**
   ```bash
   curl -X POST http://localhost:8000/ideas/{idea_id}/agent-approval \
     -H "Authorization: Bearer {token}" \
     -H "Content-Type: application/json" \
     -d '{
       "summary": "Idea aprobada por agente",
       "confidence_level": "high",
       "recommendations": []
     }'
   ```
   - Expected:
     - Status: 200 OK
     - Response confirms agent_approved = true
     - Returns updated idea object

5. **Submit Human Approval**
   ```bash
   curl -X POST http://localhost:8000/ideas/{idea_id}/technical-approval \
     -H "Authorization: Bearer {token}" \
     -H "Content-Type: application/json"
   ```
   - Expected:
     - If agent_approved = false: Status 400 with message
     - If agent_approved = true: Status 200 OK
     - Response confirms human_approved = true

6. **Download PDF**
   ```bash
   curl -X GET http://localhost:8000/ideas/{idea_id}/architecture-package-pdf \
     -H "Authorization: Bearer {token}" \
     -o architecture.pdf
   ```
   - Expected:
     - Status: 200 OK
     - Content-Type: application/pdf
     - Binary PDF file downloaded
     - File valid and readable

**Success Criteria:**
- ✅ All endpoints return correct status codes
- ✅ Approvals enforced in correct order
- ✅ Chat interactions stored
- ✅ PDF downloads with correct format
- ✅ Error messages clear and actionable

---

### Scenario 7: Performance and Stress

**Objective:** Verify system performs well under load

**Steps:**

1. **Rapid Chat Messages**
   - Send 5 messages rapidly (1 per second)
   - Expected:
     - All messages queued and processed
     - No dropped messages
     - Chat history complete
     - Response time <500ms per message

2. **Multiple Ideas in Queue**
   - Verify technical queue handles 20+ items
   - Expected: UI responsive, no lag
   - Approval workflow smooth for each item

3. **Polling Updates**
   - Make changes in one browser tab
   - Observe other tab updates (every 10 seconds)
   - Expected: Status changes propagated reliably

**Success Criteria:**
- ✅ Chat responsive with rapid messages
- ✅ Large queues handled efficiently
- ✅ Polling updates reliable
- ✅ No browser freezing or hangs

---

## Checklist for Final Validation

### Backend
- [ ] Imports successful (TechnicalChatRequest, etc.)
- [ ] All 3 endpoints callable via API
- [ ] Agent approval prevents human approval
- [ ] Chat history stored correctly
- [ ] Approval timestamps recorded
- [ ] Error messages appropriate

### Frontend
- [ ] Chat interface renders correctly
- [ ] All buttons functional
- [ ] Approval status panel displays
- [ ] Translations load properly
- [ ] PDF download enabled/disabled correctly
- [ ] No console errors

### Database
- [ ] New approval fields in IdeaCase
- [ ] Chat interactions logged
- [ ] Approval dates recorded
- [ ] Data persists across sessions

### User Experience
- [ ] Workflow clear and intuitive
- [ ] Error messages helpful
- [ ] Visual feedback for all actions
- [ ] Performance acceptable
- [ ] Mobile responsive (if applicable)

---

## Troubleshooting

### Chat Interface Not Appearing
- Verify frontend build completed: `npm run build`
- Check browser console for JavaScript errors
- Verify user has technical reviewer role

### Agent Approval Button Disabled
- Check that agent_approved field exists in database
- Verify IdeaCase model updated
- Run database migration if needed

### PDF Download Fails
- Check architecture_package exists for idea
- Verify human_approved = true
- Check file permissions in /data folder
- Review backend logs for PDF generation errors

### Translation Missing
- Search App.jsx for key name
- Verify key added to all 3 language blocks (ES, EN, PT)
- Check for typos in key names
- Clear browser cache and reload

### Approval Status Not Updating
- Check polling interval (should be 10 seconds)
- Verify loadTechnicalQueue() calls endpoint correctly
- Check network tab for failed requests
- Review API response for latest data

---

## Quick Test Suite (5 minutes)

1. Login as technical reviewer ✓
2. Open technical queue ✓
3. Chat with agent 1 message ✓
4. Approve as agent ✓
5. Approve as human ✓
6. Download PDF ✓
7. Verify rejection workflow ✓
8. Check English/Spanish translations ✓

**Expected Duration:** 5 minutes  
**Success Rate:** 100% (all 8 steps pass)

---

**Last Updated:** February 14, 2026  
**Version:** 1.0  
**Status:** Ready for Testing
