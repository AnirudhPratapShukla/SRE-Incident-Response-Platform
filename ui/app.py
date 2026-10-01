import requests
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="SRE Incident Response Platform",
    page_icon="🚨",
    layout="wide",
)


# ============================================================
# SESSION STATE
# ============================================================

if "active_incident" not in st.session_state:
    st.session_state.active_incident = None

if "last_response" not in st.session_state:
    st.session_state.last_response = None

if "workflow_source" not in st.session_state:
    st.session_state.workflow_source = None


# ============================================================
# API HELPERS
# ============================================================

def api_get(
    api_url: str,
    endpoint: str,
):
    response = requests.get(
        f"{api_url}{endpoint}",
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


def api_post(
    api_url: str,
    endpoint: str,
    payload: dict,
    timeout: int = 900,
):
    response = requests.post(
        f"{api_url}{endpoint}",
        json=payload,
        timeout=timeout,
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# DISPLAY HELPERS
# ============================================================

def display_status(
    status: str,
):
    status_upper = str(
        status or ""
    ).upper()

    if "APPROVAL" in status_upper:
        st.warning(
            f"⏸️ {status_upper}"
        )

    elif "COMPLETE" in status_upper:
        st.success(
            f"✅ {status_upper}"
        )

    elif "ERROR" in status_upper:
        st.error(
            f"❌ {status_upper}"
        )

    else:
        st.info(
            f"ℹ️ {status_upper}"
        )


def render_incident_summary(
    data: dict,
):
    st.subheader(
        "Incident Summary"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Service",
            data.get(
                "service"
            ) or "N/A",
        )

    with col2:
        st.metric(
            "Status",
            data.get(
                "status"
            ) or "N/A",
        )

    with col3:
        st.metric(
            "Risk",
            data.get(
                "risk_level"
            ) or "N/A",
        )

    incident = data.get(
        "incident"
    )

    if incident:

        st.markdown(
            "### Incident"
        )

        if isinstance(
            incident,
            dict,
        ):

            st.write(
                incident.get(
                    "incident",
                    "No incident description",
                )
            )

        else:

            st.write(
                incident
            )

        jira_key = data.get(
            "jira_issue_key"
        )

        jira_url = data.get(
            "jira_issue_url"
        )

        jira_status = data.get(
            "jira_status"
        )

        if jira_key:

            st.markdown(
                f"**Jira:** `{jira_key}`"
            )

        if jira_url:

            st.markdown(
                f"[Open Jira Incident]({jira_url})"
            )

        if jira_status:

            st.markdown(
                f"**Jira Status:** `{jira_status}`"
            )


def render_investigation(
    data: dict,
):
    st.subheader(
        "Investigation & RCA"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            "### Root Cause"
        )

        st.write(
            data.get(
                "root_cause"
            ) or "Not available"
        )

    with col2:

        st.markdown(
            "### Impact"
        )

        st.write(
            data.get(
                "impact"
            ) or "Not available"
        )

    st.markdown(
        "### Supporting Evidence"
    )

    st.write(
        data.get(
            "supporting_evidence"
        ) or "Not available"
    )


def render_safety(
    data: dict,
):
    st.subheader(
        "Safety Assessment"
    )

    col1, col2 = st.columns(2)

    with col1:

        safety_status = data.get(
            "safety_status"
        )

        if safety_status == "BLOCKED":

            st.error(
                f"🛑 Safety: {safety_status}"
            )

        elif safety_status == "APPROVED":

            st.success(
                f"✅ Safety: {safety_status}"
            )

        else:

            st.info(
                f"Safety: "
                f"{safety_status or 'N/A'}"
            )

    with col2:

        st.metric(
            "Risk Level",
            data.get(
                "risk_level"
            ) or "N/A",
        )

    st.markdown(
        "### Safety Recommendation"
    )

    st.write(
        data.get(
            "safety_recommendation"
        ) or "Not available"
    )


def render_remediation(
    data: dict,
):
    st.subheader(
        "Remediation"
    )

    simulation_mode = data.get(
        "remediation_simulation_mode",
        False,
    )

    if simulation_mode:
        st.warning(
            "🛡️ SAFE DEMO SIMULATION — NO AWS CHANGES. "
            "The remediation and recovery verification were "
            "simulated; no AWS infrastructure was modified."
        )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            "### Recommendation"
        )

        st.write(
            data.get(
                "recommendation"
            ) or "Not available"
        )

    with col2:

        st.markdown(
            "### Execution Status"
        )

        execution_status = data.get(
            "execution_status"
        )

        if execution_status:

            if execution_status.startswith(
                "EXECUTED"
            ):

                st.success(
                    execution_status
                )

            elif (
                "NOT EXECUTED"
                in execution_status
            ):

                st.warning(
                    execution_status
                )

            else:

                st.info(
                    execution_status
                )

        else:

            st.info(
                "Not executed"
            )

    st.markdown(
        "### Verification"
    )

    verification_status = data.get(
        "verification_status"
    )

    if verification_status == "VERIFIED":

        st.success(
            "✅ Recovery Verification: VERIFIED"
        )

    elif verification_status == "FAILED":

        st.error(
            "❌ Recovery Verification: FAILED"
        )

    else:

        st.info(
            "Recovery Verification: "
            f"{verification_status or 'Not run'}"
        )

    verification_message = data.get(
        "verification_message"
    )

    if verification_message:

        st.write(
            verification_message
        )

    st.markdown(
        "### Rollback Plan"
    )

    st.write(
        data.get(
            "rollback_plan"
        ) or "Not available"
    )

    remediation_plan = data.get(
        "remediation_plan"
    )

    if remediation_plan:

        with st.expander(
            "View Remediation Report"
        ):

            st.write(
                remediation_plan
            )


def render_approval_request(
    data: dict,
):
    st.subheader(
        "Human Approval"
    )

    approval_request = data.get(
        "approval_request"
    )

    if approval_request:

        st.warning(
            "The workflow is paused and "
            "requires explicit human approval."
        )

        if isinstance(
            approval_request,
            dict,
        ):

            message = (
                approval_request.get(
                    "message"
                )
            )

            if message:

                st.markdown(
                    f"**Request:** {message}"
                )

            service = (
                approval_request.get(
                    "service"
                )
            )

            if service:

                st.markdown(
                    f"**Service:** `{service}`"
                )

            root_cause = (
                approval_request.get(
                    "root_cause"
                )
            )

            if root_cause:

                st.markdown(
                    f"**Root Cause:** "
                    f"{root_cause}"
                )

            recommendation = (
                approval_request.get(
                    "recommendation"
                )
            )

            if recommendation:

                st.markdown(
                    f"**Recommendation:** "
                    f"{recommendation}"
                )

        else:

            st.write(
                approval_request
            )


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "🚨 SRE Incident Platform"
)

st.sidebar.markdown(
    """
AI-powered incident investigation
with human-approved remediation.
"""
)

api_url = st.sidebar.text_input(
    "FastAPI URL",
    value="http://127.0.0.1:8000",
)

aws_region = st.sidebar.text_input(
    "AWS Region",
    value="us-east-1",
)

st.sidebar.divider()

if st.sidebar.button(
    "Check API Health",
    use_container_width=True,
):

    try:

        health = api_get(
            api_url,
            "/health",
        )

        if health.get(
            "status"
        ) == "healthy":

            st.sidebar.success(
                "API is healthy"
            )

        else:

            st.sidebar.warning(
                str(health)
            )

    except Exception as exc:

        st.sidebar.error(
            f"API unavailable: {exc}"
        )


# ============================================================
# HEADER
# ============================================================

st.title(
    "🚨 SRE Incident Response Platform"
)

st.markdown(
    """
**CloudWatch → Jira → LangGraph → RAG → RCA → Safety
→ Human Approval → Controlled Remediation → Verification**
"""
)

st.divider()


# ============================================================
# DASHBOARD TABS
# ============================================================

tab1, tab2, tab3 = st.tabs(
    [
        "📊 Dashboard",
        "📝 Manual Incident",
        "☁️ CloudWatch",
    ]
)


# ============================================================
# DASHBOARD
# ============================================================

with tab1:

    st.header(
        "Incident Dashboard"
    )

    active = (
        st.session_state.active_incident
    )

    if not active:

        st.info(
            "No active incident. "
            "Create a manual incident "
            "or scan CloudWatch."
        )

    else:

        render_incident_summary(
            active
        )

        st.divider()

        display_status(
            active.get(
                "status"
            )
        )

        # ====================================================
        # HUMAN APPROVAL
        # ====================================================

        if active.get(
            "status"
        ) == "approval_required":

            render_approval_request(
                active
            )

            st.divider()

            st.markdown(
                "### Controlled Remediation"
            )

            st.info(
                "Only explicitly supported "
                "remediation actions can be executed."
            )

            remediation_action = (
                st.selectbox(
                    "Remediation Action",
                    options=[
                        "reboot_ec2",
                    ],
                    help=(
                        "Select the controlled AWS "
                        "action that will be executed "
                        "after approval."
                    ),
                )
            )

            remediation_instance_id = (
                st.text_input(
                    "Target EC2 Instance ID",
                    placeholder=(
                        "i-0123456789abcdef0"
                    ),
                    help=(
                        "Required for reboot_ec2. "
                        "For safe demo mode, use a synthetic "
                        "instance ID such as "
                        "i-0123456789abcdef0."
                    ),
                )
            )

            simulation_mode = st.checkbox(
                "🛡️ SAFE DEMO SIMULATION",
                value=True,
                help=(
                    "When enabled, the remediation is simulated "
                    "and no AWS infrastructure is modified. "
                    "Disable only when you intentionally want "
                    "to execute the real MCP-controlled action."
                ),
            )

            if simulation_mode:
                st.warning(
                    "🛡️ SAFE DEMO MODE ENABLED — NO AWS CHANGES. "
                    "Approval will execute the remediation workflow "
                    "using simulation only."
                )
            else:
                st.error(
                    "⚠️ REAL MCP EXECUTION ENABLED. "
                    "Approving may modify AWS infrastructure."
                )

            st.warning(
                "⚠️ Human approval is required "
                "before any controlled remediation "
                "is attempted."
            )

            st.divider()

            st.markdown(
                "### Approval Decision"
            )

            col1, col2 = st.columns(2)

            # ------------------------------------------------
            # APPROVE
            # ------------------------------------------------

            with col1:

                if st.button(
                    "✅ Approve Remediation",
                    use_container_width=True,
                ):

                    if (
                        remediation_action
                        == "reboot_ec2"
                        and not (
                            remediation_instance_id
                            .strip()
                        )
                    ):

                        st.error(
                            "Enter an EC2 instance ID "
                            "before approving."
                        )

                    else:

                        thread_id = active.get(
                            "thread_id"
                        )

                        try:

                            with st.spinner(
                                "Resuming LangGraph workflow..."
                            ):

                                result = api_post(
                                    api_url,
                                    (
                                        f"/incident/"
                                        f"{thread_id}"
                                        f"/approve"
                                    ),
                                    {
                                        "decision": "yes",

                                        "remediation_action": (
                                            remediation_action
                                        ),

                                        "remediation_instance_id": (
                                            remediation_instance_id.strip()
                                        ),

                                        "simulation_mode": (
                                            simulation_mode
                                        ),
                                    },
                                )

                            st.session_state.active_incident = (
                                result
                            )

                            st.session_state.last_response = (
                                result
                            )

                            st.rerun()

                        except Exception as exc:

                            st.error(
                                f"Approval failed: {exc}"
                            )

            # ------------------------------------------------
            # REJECT
            # ------------------------------------------------

            with col2:

                if st.button(
                    "❌ Reject Remediation",
                    use_container_width=True,
                ):

                    thread_id = active.get(
                        "thread_id"
                    )

                    try:

                        with st.spinner(
                            "Rejecting remediation..."
                        ):

                            result = api_post(
                                api_url,
                                (
                                    f"/incident/"
                                    f"{thread_id}"
                                    f"/approve"
                                ),
                                {
                                    "decision": "no",
                                },
                            )

                        st.session_state.active_incident = (
                            result
                        )

                        st.session_state.last_response = (
                            result
                        )

                        st.rerun()

                    except Exception as exc:

                        st.error(
                            f"Rejection failed: {exc}"
                        )

        # ====================================================
        # COMPLETED / NORMAL WORKFLOW
        # ====================================================

        else:

            render_investigation(
                active
            )

            st.divider()

            render_safety(
                active
            )

            st.divider()

            render_remediation(
                active
            )

        # ====================================================
        # RAW RESPONSE
        # ====================================================

        if st.session_state.last_response:

            with st.expander(
                "View Raw API Response"
            ):

                st.json(
                    st.session_state.last_response
                )


# ============================================================
# MANUAL INCIDENT
# ============================================================

with tab2:

    st.header(
        "Create Manual Incident"
    )

    st.markdown(
        """
Use this to start the LangGraph investigation
without waiting for a real CloudWatch alarm.
"""
    )

    with st.form(
        "manual_incident_form"
    ):

        service = st.text_input(
            "Service",
            value="order-api",
        )

        incident = st.text_area(
            "Incident Description",
            value=(
                "The order-api service is "
                "returning HTTP 500 errors "
                "and requests are timing out."
            ),
            height=120,
        )

        submitted = st.form_submit_button(
            "🚀 Start Investigation",
            use_container_width=True,
        )

    if submitted:

        if not service.strip():

            st.error(
                "Service is required."
            )

        elif not incident.strip():

            st.error(
                "Incident description is required."
            )

        else:

            try:

                with st.spinner(
                    "Running incident investigation..."
                ):

                    result = api_post(
                        api_url,
                        "/incident",
                        {
                            "incident": incident,
                            "service": service,
                        },
                    )

                st.session_state.active_incident = (
                    result
                )

                st.session_state.last_response = (
                    result
                )

                st.session_state.workflow_source = (
                    "Manual Incident"
                )

                st.success(
                    "Incident workflow started."
                )

                st.rerun()

            except Exception as exc:

                st.error(
                    f"Incident creation failed: {exc}"
                )


# ============================================================
# CLOUDWATCH
# ============================================================

with tab3:

    st.header(
        "☁️ CloudWatch Incident Detection"
    )

    st.markdown(
        """
Scan the configured AWS region for CloudWatch
alarms currently in the ALARM state.
"""
    )

    st.info(
        f"Region: `{aws_region}`"
    )

    if st.button(
        "🔍 Scan CloudWatch",
        use_container_width=True,
    ):

        try:

            with st.spinner(
                "Checking CloudWatch and "
                "starting incident workflows..."
            ):

                result = api_post(
                    api_url,
                    "/cloudwatch/incidents",
                    {
                        "region_name": aws_region,
                    },
                )

            st.session_state.last_response = (
                result
            )

            if result.get(
                "status"
            ) == "no_incidents":

                st.success(
                    "No active CloudWatch "
                    "incidents detected."
                )

            else:

                st.success(
                    f"Detected "
                    f"{result.get('incidents_detected', 0)} "
                    f"incident(s)."
                )

                incidents = result.get(
                    "incidents",
                    [],
                )

                if incidents:

                    first_incident = (
                        incidents[0]
                    )

                    st.session_state.active_incident = {
                        "status": first_incident.get(
                            "status"
                        ),

                        "thread_id": first_incident.get(
                            "thread_id"
                        ),

                        "incident": first_incident.get(
                            "incident"
                        ),

                        "approval_request": first_incident.get(
                            "approval_request"
                        ),
                    }

                    st.session_state.workflow_source = (
                        "CloudWatch"
                    )

                    st.rerun()

        except Exception as exc:

            st.error(
                f"CloudWatch scan failed: {exc}"
            )

    if (
        st.session_state.workflow_source
        == "CloudWatch"
    ):

        st.markdown(
            "### CloudWatch Workflow"
        )

        active = (
            st.session_state.active_incident
        )

        if active:

            render_incident_summary(
                active
            )

            if active.get(
                "approval_request"
            ):

                render_approval_request(
                    active
                )