import asyncio
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters

from catalog.search import search_courses


async def check_server() -> None:
    project = Path(__file__).resolve().parents[1]
    expected = [course.model_dump(mode="json") for course in search_courses("python")]
    assert [course["code"] for course in expected] == ["PY01", "PY02"]
    assert len(search_courses("python", project / "data" / "extra_courses.json")) == 3
    server = StdioServerParameters(
        command=sys.executable,
        args=[str(project / "server.py")],
        cwd=str(project.parent),
    )
    async with Client(server) as client:
        tools = await client.list_tools()
        assert [tool.name for tool in tools.tools] == ["find_courses"]
        result = await client.call_tool("find_courses", {"query": "python"})
        assert not result.is_error
        assert result.structured_content == {"result": expected}
        empty = await client.call_tool("find_courses", {"query": "astronomy"})
        assert not empty.is_error
        assert empty.structured_content == {"result": []}
        invalid = await client.call_tool("find_courses", {"query": " "})
        assert invalid.is_error
        again = await client.call_tool("find_courses", {"query": "python"})
        assert not again.is_error
        assert again.structured_content == {"result": expected}


def test_real_stdio_server() -> None:
    asyncio.run(check_server())
