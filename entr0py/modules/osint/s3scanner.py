"""entr0py.modules.osint.s3scanner — S3 bucket enumeration and misconfiguration check."""
from __future__ import annotations
from typing import Any, AsyncIterator
from entr0py.core.base import Category, Module, ModuleMeta, Option, OptionType


class S3Scanner(Module):
    meta = ModuleMeta(
        name="S3Scanner",
        slug="s3scanner",
        description=(
            "Scan for open/misconfigured S3 buckets and other cloud storage "
            "(GCP, Azure, DigitalOcean). Checks read/write permissions."
        ),
        category=Category.OSINT,
        author="sa7mon",
        version="3.x",
        tags=["s3", "cloud", "bucket", "misconfiguration", "osint"],
        packages=["s3scanner"],
        tools=["s3scanner"],
    )

    def options(self) -> list[Option]:
        return [
            Option("bucket",   "",         "Single bucket name to scan",
                   required=False, default=""),
            Option("input",    "--buckets-file", "File containing bucket names",
                   required=False, default=""),
            Option("provider", "--provider", "Cloud provider (aws|gcp|azure|digitalocean|dreamhost|linode)",
                   type=OptionType.CHOICE,
                   choices=["aws", "gcp", "azure", "digitalocean", "dreamhost", "linode"],
                   required=False, default="aws"),
            Option("threads",  "--threads", "Concurrency",
                   type=OptionType.INTEGER, required=False, default=4),
        ]

    async def run(self, opts: dict[str, Any]) -> AsyncIterator[str]:
        if not opts.get("bucket") and not opts.get("input"):
            yield "[!] Provide either 'bucket' (single) or 'input' (file)."
            return
        cmd = ["s3scanner", "--provider", opts.get("provider", "aws"),
               "--threads", str(opts.get("threads", 4))]
        if opts.get("bucket"):
            cmd += ["scan", "--bucket", opts["bucket"]]
        else:
            cmd += ["scan", "--buckets-file", opts["input"]]
        async for line in self._exec(cmd):
            yield line
