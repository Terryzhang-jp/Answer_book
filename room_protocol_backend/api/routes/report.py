from fastapi import APIRouter, HTTPException
from loguru import logger

from core.models.report import ReportRequest, ReportResponse, ReportData
from core.services.report.report_service import report_service

router = APIRouter()

@router.post("/generate", response_model=ReportResponse)
async def generate_report(request: ReportRequest):
    """生成对话分析报告"""
    try:
        logger.info(f"收到报告生成请求 - 线程ID: {request.thread_id}, 用户ID: {request.user_id}")
        
        # 启动异步报告生成
        task_id = await report_service.generate_report_async(request)
        
        return ReportResponse(
            success=True,
            task_id=task_id,
            message="报告生成任务已启动"
        )
        
    except Exception as e:
        logger.error(f"报告生成请求失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"报告生成失败: {str(e)}")

@router.get("/status/{task_id}")
async def get_report_status(task_id: str):
    """获取报告生成状态"""
    try:
        report = report_service.get_report_status(task_id)
        
        if not report:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        return {
            "success": True,
            "status": report.status,
            "report_id": report.id,  # 始终返回report_id
            "current_section": getattr(report, 'current_section', 0),
            "completed_sections": getattr(report, 'completed_sections', []),
            "error_message": report.error_message if report.status == "failed" else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取报告状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取状态失败: {str(e)}")

@router.get("/thread/{thread_id}")
async def get_report_by_thread_id(thread_id: str):
    """通过线程ID获取报告"""
    try:
        report = report_service.get_report_by_thread_id(thread_id)

        if not report:
            raise HTTPException(status_code=404, detail="该对话暂无报告")

        if report.status != "completed":
            raise HTTPException(status_code=400, detail="报告尚未完成")

        return {
            "success": True,
            "report": report.dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"通过线程ID获取报告失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取报告失败: {str(e)}")

@router.get("/{report_id}")
async def get_report(report_id: str):
    """获取完整报告"""
    try:
        report = report_service.get_report_by_id(report_id)

        if not report:
            raise HTTPException(status_code=404, detail="报告不存在")

        if report.status != "completed":
            raise HTTPException(status_code=400, detail="报告尚未完成")

        return {
            "success": True,
            "report": report.dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取报告失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取报告失败: {str(e)}")
