package com.defamation.backend.web;

import com.defamation.backend.service.CaseService;
import com.defamation.backend.web.dto.CaseDto;
import com.defamation.backend.web.dto.PageResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/cases")
@RequiredArgsConstructor
public class CaseController {

    private final CaseService caseService;

    @GetMapping
    public PageResponse<CaseDto> getCases(
            @RequestParam(name = "page", defaultValue = "0") int page,
            @RequestParam(name = "size", defaultValue = "10") int size,
            @RequestParam(name = "q", required = false) String q
    ) {
        return caseService.searchCases(q, page, size);
    }
}
